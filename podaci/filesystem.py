import hashlib
import os, os.path, shutil, sys
import magic
import zipfile
import StringIO
import logging
from datetime import datetime
from copy import deepcopy
import elasticsearch
from distutils.version import StrictVersion
from uuid import uuid4

from settings.settings import PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT

def random_id():
    return str(uuid4())

class AuthenticationError(Exception):
    def __str__(self):
        return "Access denied"

class FileNotFound(Exception):
    def __str__(self):
        return "[File not found]"


def sha256sum(filename, blocksize=65536):
    f = None
    if type(filename) in [str, unicode]:
        f = open(filename, "r+b")
    else:
        f = filename
    
    hash = hashlib.sha256()
    for block in iter(lambda: f.read(blocksize), ""):
        hash.update(block)

    f.seek(0)
    return hash.hexdigest()

COMMON_METADATA_V1 = {
    "name":                 "",     # Everything should have a name
    "date_added":           "",
    "changelog":            [],
    "notes":                [],
    "public_read":          False,  # Whether to allow public read access
    "staff_allowed":        False,  # Whether to override to allow all staff to do anything
    "allowed_users":        [],
    "allowed_write_users":  [],
}

FILE_METADATA_V1 = {
    "schema_version":       1,
    "url":                  "",
    "title":                "",
    "date_added":           "",
    "tags":                 [],
    "text":                 "",
    "allowed_users":        [],
    "allowed_groups":       [],
    "metadata":             {},
}

FILE_METADATA_V2 = {
    "identifier":           "",     # Project-User-6 digits of SHA256
    "created_by":           "",     # User ID
    "schema_version":       2,      # Always version 2
    "is_resident":          True,
    "filename":             "",     # Used if file is resident
    "url":                  "",     # Used if file is non-resident
    "title":                "",
    "hash":                 "",     # Required for resident files
    "size":                 0,      # Size in bytes
    "tags":                 [],
    "mimetype":             "",
    "description":          "",
    "text":                 "",     # Extracted 
    "annotations":          [],
    "is_indexed":           False,
    "extra":                {},     # Any extra structured metadata
}
FILE_METADATA_V2.update(COMMON_METADATA_V1)

TAG_METADATA_V1 = {
    "parents":              [],
    "icon":                 "default",
}
TAG_METADATA_V1.update(COMMON_METADATA_V1)

class MetaMixin:
    """
    The Meta Mixin provides objects with the ability to store metadata and 
    synchronize it with an Elasticsearch server. It also manages permissions.
    """
    def __getitem__(self, item):
        return self.meta[item]

    def __setitem__(self, item, value):
        self.meta[item] = value
        self.sync()

    def _load_metadata(self):
        """Load metadata from server."""
        if not self.id: raise ValueError("Cannot get descriptor without an id")
        try:
            self.meta.update(self.fs.es.get(index=self.fs.es_index, doc_type=self.DOCTYPE, id=self.id)["_source"])
            self.exists = True
        except:
            raise FileNotFound()
        return self.meta

    def to_json(self):
        """Get a JSON blob containing the ID and the object's metadata."""
        return {"id": self.id, "meta": self.meta}

    def details_string(self):
        """Return a formatted details string that describes the object's permissions."""
        s = "%s%s %3dU %3dW %3dN" % (
            ["-","P"][self["public_read"]], 
            ["-","S"][self["staff_allowed"]], 
            len(self["allowed_users"]), 
            len(self["allowed_write_users"]), 
            len(self["notes"]))
        if self.DOCTYPE == "tag":
            s += " %4dF" % (self.fs.list_files(self.id)[0])
        return s

    def log(self, message, sync=False):
        """Add a log entry. Specify sync=True to synchronize immediately."""
        if self.fs.user:
            uid = self.fs.user.id
        else:
            uid = None

        self.meta["changelog"].append({
                "date": datetime.now().isoformat(), 
                "user": uid,
                "message": message
            })
        if sync:
            self._sync()

    def _create_index(self, id=None):
        """Adds an index entry to the Elasticsearch database."""
        if not self.fs.user:
            raise AuthenticationError()
        if not id and self.id:
            id = self.id
        res = self.fs.es.create(index=self.fs.es_index, doc_type=self.DOCTYPE, body=self.meta, id=id)
        if res["created"]:
            self.id = res["_id"]
            self.version = res["_version"]
            self.exists = True

    def _index_get_json(self):
        return {
            "_index": self.fs.es_index,
            "_type": self.DOCTYPE,
            "_id": self.id,
            "_source": self.meta,
        }

    def _create_index_lazy(self):
        """Instead of creating the index right now, we add it to a bulk loader."""
        if not self.fs.user:
            raise AuthenticationError()
        if not self.id:
            raise ValueError("ID must be set when doing bulk loads.")
        if not hasattr(self, "lazy_index_cache"):
            self.lazy_index_cache = []

        act = self._index_get_json()
        self.lazy_index_cache.append(act)

        if len(self.lazy_index_cache) >= 500:
            self._flush_lazy_indexer()

    def _flush_lazy_indexer(self):
        """Make sure bulk indexing comands have fired."""
        res = elasticsearch.helpers.streaming_bulk(
                    client=self.fs.es, 
                    actions=self.lazy_index_cache)
        print "Performed %d actions lazily" % len(self.lazy_index_cache)
        self.lazy_index_cache = []

    def _create_metadata(self):
        """Creates a default metadata template for a new entry."""
        self.meta = deepcopy(self.METADATA_TEMPLATE)
        self.meta["date_added"] = datetime.now().isoformat()
        self.log("Created")
        if self.fs.user:
            self.meta["allowed_users"].append(self.fs.user.id)
            self.meta["allowed_write_users"].append(self.fs.user.id)

    def _sync(self, override=False):
        """Updates an index entry in the Elasticsearch database."""
        if not override and not self.has_write_permission(self.fs.user):
            raise AuthenticationError()
        if not self.id: return
        result = self.fs.es.update(
                index=self.fs.es_index, 
                doc_type=self.DOCTYPE, 
                id=self.id, 
                body={"doc": self.meta, "detect_noop": True}
            )
        return result

    def add_user(self, user, write=False):
        """Give a user permissions on the object."""
        if not user: return
        if user.id not in self.meta["allowed_users"]:
            self.meta["allowed_users"].append(user.id)
        if write and user.id not in self.meta["allowed_write_users"]:
            self.meta["allowed_write_users"].append(user.id)
        self.log("Added user '%s' [%d] (write=%s)" % (user.email, user.id, write))
        self._sync()

    def remove_user(self, user):
        """Revoke user permissions."""
        if not user: return
        try:
            self.meta["allowed_users"].remove(user.id)
            self.meta["allowed_write_users"].remove(user.id)
            self.log("Removed user '%s' [%d]" % (user.email, user.id))
            self._sync(override=True)
        except ValueError:
            pass

    def make_public(self):
        """Allow public reads."""
        self.meta["public_read"] = True
        self.log("Made file public.")
        self._sync()

    def make_private(self):
        """Disallow public reads."""
        self.meta["public_read"] = False
        self.log("Made file private.")
        self._sync()

    def allow_staff(self):
        """Allow all staff members to access (read/write)"""
        self.meta["staff_allowed"] = True
        self.log("Made file accessible to all staff.")
        self._sync()

    def disallow_staff(self):
        """Disallow staff to access"""
        self.meta["staff_allowed"] = False
        self.log("Made file inaccessible to staff.")
        self._sync()

    def has_permission(self, user):
        """Check if a given user has read permission."""
        if user.is_superuser: return True
        if self.meta["public_read"]: return True
        if self.meta["staff_allowed"] and user.is_staff: return True
        if user.id in self.meta["allowed_users"]: return True
        if self.DOCTYPE == "file":
            for t in self.meta["tags"]:
                tag = Tag(self.fs, tid=t)
                if tag.has_permission(user):
                    return True
        return False

    def has_write_permission(self, user):
        """Check if a given user has write permission."""
        if user.is_superuser: return True
        if user.id in self.meta["allowed_write_users"]: return True
        if self.meta["staff_allowed"] and user.is_staff: return True
        if self.DOCTYPE == "file":
            for t in self.meta["tags"]:
                tag = Tag(self.fs, tid=t)
                if tag.has_write_permission(user):
                    return True
        return False


class Tag(MetaMixin):
    DOCTYPE = "tag"
    METADATA_TEMPLATE = TAG_METADATA_V1

    def __init__(self, fs, tid=None, name=None, prepopulate_meta={}):
        self.fs = fs
        self.id = tid
        self.meta = deepcopy(self.METADATA_TEMPLATE)
        self.meta.update(prepopulate_meta)
        if self.id and not prepopulate_meta:
            self._load_metadata()

    def __unicode__(self):
        if not self.id: return "[Uninitialized tag object]"
        if not self.meta: self._load_metadata()
        return "[Tag %s] %s" % (self.id, self.meta.get("name"))

    def __str__(self):
        return self.__unicode__()

    def load(self, tid):
        self.id = tid
        self._load_metadata()

    def create(self, name):
        """Create a new tag, given a name."""
        self._create_metadata()
        self.meta["name"] = name
        self._create_index()
        return self.id, self.meta, True

    def delete(self, sure=False):
        """Delete the current tag."""
        if not self.id: raise ValueError("No tag specified")
        if not sure: raise ValueError("You don't seem to be sure. (try sure=True)")
        self.fs.es.delete(index=self.fs.es_index, doc_type="tag", id=self.id)
        return True

    def parent_add(self, parenttag):
        """Add a parent tag."""
        if isinstance(parenttag, Tag): parenttag = parenttag.id
        if parenttag not in self.meta["parents"]:
            self.meta["parents"].append(parenttag)
        self._sync()

    def parent_remove(self, parenttag):
        """Disown a parent tag."""
        self.meta["parents"].remove(parenttag)
        self._sync()

    def child_add(self, childtag):
        """Add a child tag."""
        raise NotImplementedError()
        #if isinstance(childtag, Tag): childtag = childtag.id
        #if self.id not in self.meta["parents"]:
        #    self.meta["parents"].append(parenttag)
        #self._sync()

    def child_remove(self, childtag):
        """Disown a child tag."""
        raise NotImplementedError()

    def child_create(self, name):
        """Create a new child tag."""
        raise NotImplementedError()

    def list_files(self, _from=0, _size=1000):
        """Return a list of existing files"""
        if not self.has_permission(self.fs.user):
            raise AuthenticationError("User %s has no access to file %s" % (self.fs.user, self.id))

        # TODO: Limit this to only include files the user can see.
        body = {"query":{"match":{"tags": self.id}}}
        res = self.fs.es.search(index=self.fs.es_index, doc_type="file", body=body, from_=_from, size=_size)
        return res["hits"]["total"], [File(self.fs, filemeta["_id"], prepopulate_meta=filemeta["_source"]) for filemeta in res["hits"]["hits"]]

    def list_children(self):
        """Get a list of all children of this tag."""
        raise NotImplementedError()

    def list_parents(self):
        """Get a list of all parents of this tag."""
        raise NotImplementedError()

    def get_zip(self):
        """Return a Zip file containing the files in this tag. Limited to 50MB archives."""
        # To prevent insane loads, we're going to limit this to 50MB archives for now.
        _50MB = 50 * 1024 * 1024
        files = self.get_files()[1]
        totalsize = sum([x.meta.get("size", 0) for x in files])
        if totalsize > _50MB:
            return False

        zstr = StringIO.StringIO()
        with zipfile.ZipFile(zstr, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f.resident_location(), f.meta["filename"])
        zstr.seek(0)
        return zstr

    def has_files(self):
        """Return the number of files associated with this tag."""
        body = {"query":{"match":{"tags": self.id}}}
        res = self.fs.es.search(index=self.fs.es_index, doc_type="file", body=body)
        return res["hits"]["total"]


class File(MetaMixin):
    DOCTYPE = "file"
    METADATA_TEMPLATE = FILE_METADATA_V2
    def __init__(self, fs, fid=None, prepopulate_meta={}):
        self.fs = fs
        self.id = fid
        self.exists = False
        self.load_by_id(fid, prepopulate_meta)

    def __unicode__(self):
        if not self.id: return "[Uninitialized file object]"
        if not self.meta: self._load_metadata()
        return "[File %s] %s title='%s', mimetype='%s', tags='%s', is_resident='%s'." % (
            self.id, 
            "filename='%s'" % self.meta.get("filename") if self.meta.has_key("filename") else
            "url='%s'" % self.meta.get("url"),
            self.meta.get("title", ""), self.meta.get("mimetype", ""), 
            self.meta.get("tags", []), self.meta.get("is_resident", False))

    def __str__(self):
        return self.__unicode__()

    def get_filehandle(self):
        """Get a file handle to the file itself."""
        if not self.has_permission(self.fs.user):
            raise AuthenticationError("User %s has no access to file %s" % (self.fs.user, self.id))
        if not self.id: raise ValueError("Cannot get file without an id")
        if self.meta["is_resident"]:
            return open(self.resident_location())
        else:
            return urllib2.urlopen(self.meta["url"])

    def resident_location(self):
        """Return the resident location of the file."""
        if self.meta["hash"] == "": raise Exception("File hash missing")
        if self.meta["filename"] == "": raise Exception("Filename missing")
        hashdirs = os.path.join(*map(lambda x,y: x+y, *([iter(self.meta["hash"])] * 2))[:3])
        directory = os.path.join(self.fs.data_root, hashdirs)
        try:
            os.makedirs(directory)
        except os.error:
            pass
        return os.path.join(directory, self.meta["filename"])

    def _build_index(self):
        """Reads the file and tries basic details extraction."""
        pass

    def create_from_filehandle(self, fh, filename=None):
        """Given a file handle, create a file."""
        self._create_metadata()
        if not filename:
            filename = fh.name
        if not filename:
            filename = "Untitled file"
        self.meta["filename"] = filename
        self.meta["hash"] = sha256sum(fh)
        self.meta["mimetype"] = magic.Magic(mime=True).from_buffer(fh.read(100))
        #if self.exists_by_hash(self.meta["hash"]):
        #    self.load_by_hash(self.meta["hash"])
        #    if (self.fs.user):
        #        self.add_user(self.fs.user)
        #    return self.id, self.meta, False

        fh.seek(0)
        f = open(self.resident_location(), "w+")
        f.write(fh.read())
        f.close()

        self.meta["size"] = os.stat(self.resident_location()).st_size

        self._build_index()
        self._create_index()

        return self.id, self.meta, True

    def create_from_path(self, filename, filename_override=None):
        """Given a file path, create a file."""
        if not os.path.isfile(filename): raise ValueError("File does not exist")
        self._create_metadata()
        self.meta["filename"] = os.path.split(filename)[-1]
        if filename_override:
            self.meta["filename"] = filename_override
        self.meta["hash"] = sha256sum(filename)
        self.meta["mimetype"] = magic.Magic(mime=True).from_file(filename)
        #if self.exists_by_hash(self.meta["hash"]):
        #    print "Warning: File exists!"
        #    self.load_by_hash(self.meta["hash"])
        #    if (self.fs.user):
        #        self.add_user(self.fs.user)
        #    return self.id, self.meta, False

        shutil.copy(filename, self.resident_location())
        self.meta["size"] = os.stat(self.resident_location()).st_size
        self._build_index()
        self._create_index()

        return self.id, self.meta, True

    def create_from_url(self, url, make_resident=False):
        """Given a URL, create a file. Optionally, make the file resident."""
        self._create_metadata()
        self.meta["url"] = url
        self.meta["is_resident"] = False
        if self.exists_by_url(self.meta["url"]):
            return None, None, False

        self._build_index()
        self._create_index()

        if make_resident:
            self._make_resident()

        return self.id, self.meta, True

    def load(self, fid, prepopulate_meta={}):
        """Synonym of load_by_id"""
        return self.load_by_id(fid, prepopulate_meta)

    def load_by_id(self, fid, prepopulate_meta={}):
        """Loads a file by ID into this File object."""
        self.id = fid
        self.meta = deepcopy(self.METADATA_TEMPLATE)
        self.meta.update(prepopulate_meta)
        if self.id and not prepopulate_meta:
            self._load_metadata()

    def load_by_hash(self, sha):
        # TODO: Make this work
        body = {"query":{"match":{"hash":sha}}}
        res = self.fs.es.search(index=self.fs.es_index, doc_type="file", body=body)
        if len(res["hits"]["hits"]) == 0: return FileNotFound()
        return self.load_by_id(res["hits"]["hits"][0]["_id"])

    def exists_by_hash(self, sha):
        body = {"query":{"match":{"hash":sha}}}
        try:
            res = self.fs.es.search_exists(index=self.fs.es_index, doc_type="file", body=body)
        except elasticsearch.exceptions.NotFoundError, e:
            return False
        return res["exists"]

    def exists_by_url(self, url):
        body = {"query":{"match":{"url":url}}}
        try:
            res = self.fs.es.search_exists(index=self.fs.es_index, doc_type="file", body=body)
        except elasticsearch.exceptions.NotFoundError, e:
            return False
        return res["exists"]

    def _make_resident(self, buf=None):
        """Makes a resident copy of an URL-based file entry."""
        raise NotImplementedError()
        self.meta["is_resident"] = True

    def delete(self, sure=False):
        """Delete a file. Make sure you're sure."""
        if not self.id: raise ValueError("No file specified")
        if not sure: raise ValueError("You don't seem to be sure. (try sure=True)")
        if self.meta["filename"]:
            try:
                os.unlink(self.resident_location())
            except OSError:
                pass
        self.fs.es.delete(index=self.fs.es_index, doc_type="file", id=self.id)
        self.exists = False
        return True

    def add_tag(self, tag):
        """Add a tag to a file."""
        if isinstance(tag, Tag): tag = tag.id
        if tag in self.meta["tags"]: return
        self.meta["tags"].append(tag)
        self.log("Added tag '%s'" % tag)
        self._sync()

    def remove_tag(self, tag):
        """Remove a tag from a file."""
        if isinstance(tag, Tag): tag = tag.id
        self.meta["tags"].remove(tag)
        self.log("Removed tag '%s'" % tag)
        self._sync()

    def add_note(self, text):
        return self.note_add(text)

    def note_add(self, text):
        """Add a note to a file."""
        note = {
            "id": random_id(),
            "user": self.fs.user.id,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "text": text,
            "score": 0,
        }
        self.meta["notes"].append(note)
        self.log("Added note")
        return self._sync()

    def note_delete(self, nid):
        """Delete a note from a file."""
        for i in range(0, len(self.meta["notes"])):
            if self.meta["notes"][i]["id"] == nid:
                del(self.meta["notes"][i])
                return self._sync()
        return False

    def note_update(self, nid, text):
        """Delete a note from a file."""
        assert(self.fs.user.is_superuser)
        for i in range(0, len(self.meta["notes"])):
            if self.meta["notes"][i]["id"] == nid:
                assert(self.fs.user.id == self.meta["notes"][i]["user"])
                self.meta["notes"][i]["text"] = text
                self.meta["notes"][i]["modified"] = datetime.now().isoformat()
                return self._sync()
        return False

    def note_list(self):
        """Get a list of notes."""
        return self.meta["notes"]

    def get_thumbnail(self, width=680, height=460):
        """Return a thumbnail of a file."""
        # Todo: Perhaps this belongs elsewhere?
        if self.meta["mimetype"]:
            basetype, subtype = self.meta["mimetype"].split("/")
        else:
            return False

        if basetype == "image":
            # We are dealing with an image!
            #from PIL import Image
            #i = Image.open(self.resident_location())
            #i.thumbnail((width,height), Image.ANTIALIAS)
            return False
        elif basetype == "application":
            return False
        # TODO: Build me
        return False

    def get_thumbnail_as_img_tag(self):
        img = self.get_thumbnail()
        if img:
            return '<img src="%s"/>' % img
        else:
            return ''


class FileSystem:
    def __init__(self, es_servers=PODACI_SERVERS, es_index=PODACI_ES_INDEX, data_root=PODACI_FS_ROOT, user=None):
        self.es_servers = es_servers
        self.es_index = es_index
        self.data_root = data_root
        self.user = user
        self.connect()

    def connect(self):
        self.es = elasticsearch.Elasticsearch(self.es_servers)
        # Get version info:
        info = self.es.info()
        ver = StrictVersion(info["version"]["number"])
        if ver < StrictVersion("1.4.0"):
            raise Exception("Podaci requires an ElasticSearch server version >= 1.4.0")

        # Guarantee that the index exists...
        if not self.es.indices.exists(index=self.es_index):
            self.es.indices.create(index=self.es_index, ignore=400)

            print "#"*50
            print "## %-44s ##" % ""
            print "## %-44s ##" % "Initialized ElasticSearch Index"
            print "## %-44s ##" % ""
            print "#"*50

    def _get_total_filesystem_size(self):
        body = {
            "query" : {
                "match_all" : {} 
            },
            "aggs" : {
                "size" : { "sum" : { "field" : "size" } }
            }
        }
        res = self.es.search(index=self.es_index, doc_type="file", body=body)
        return res["aggregations"]["size"]["value"]

    def status(self):
        stat = {}

        stat["data_root"] = self.data_root
        stat["servers"] = self.es_servers
        stat["index"] = self.es_index
        stat["cluster"] = self.es.cluster.state()
        stat["size"] = self._get_total_filesystem_size()
        stat["files"] = self.es.count(index=self.es_index, doc_type="file")["count"]
        stat["tags"] = self.es.count(index=self.es_index, doc_type="tag")["count"]
        return stat


    def list_user_tags(self, user, root=None, _from=0, _size=1000):
        # TODO: Decide if this is okay
        if root:
            body = {
                    "query": {
                        "bool": {
                            "must": [
                                #{"match":{"allowed_users":user.id}},
                                {"match":{"parents":root}}
                            ]
                        }
                    }
                }
        elif root == False: # Explicitly disallow non-root items
            body = {
                    "query": {
                        "match": {"allowed_users": user.id}
                    },
                    "filter": {
                        "missing": {"field": "parents"}
                    }
                }
        else:
            body = {"query":{"match":{"allowed_users":user.id}}}
        res = self.es.search(index=self.es_index, doc_type="tag", body=body, from_=_from, size=_size)
        return res["hits"]["total"], [Tag(self, tagmeta["_id"], prepopulate_meta=tagmeta["_source"]) for tagmeta in res["hits"]["hits"]]

    def list_tags(self, _from=0, _size=1000):
        # TODO: Decide if this is okay.
        body = {}
        res = self.es.search(index=self.es_index, doc_type="tag", body=body, from_=_from, size=_size)
        return res["hits"]["total"], [Tag(self, tagmeta["_id"], prepopulate_meta=tagmeta["_source"]) for tagmeta in res["hits"]["hits"]]

    def list_user_files(self, user, root=None, _from=0, _size=1000):
        # TODO: Decide if this is okay.
        if root:
            body = {"query":{"bool":
                    {"must":
                        [
                            {"match":{"allowed_users":user.id}},
                            {"match":{"tags":root}}
                        ]
                    }
                }}
        else:
            body = {"query":{"match":{"allowed_users":user.id}}}
        res = self.es.search(index=self.es_index, doc_type="file", body=body, from_=_from, size=_size)
        return res["hits"]["total"], [File(self, filemeta["_id"], prepopulate_meta=filemeta["_source"]) for filemeta in res["hits"]["hits"]]

    def search_files(self, query, _from=0, _size=1000):
        # TODO: Decprecated. Make Search class?
        res = self.es.search(index=self.es_index, doc_type="file", body=query, from_=_from, size=_size)
        return res["hits"]["total"], [File(self, filemeta["_id"], prepopulate_meta=filemeta["_source"]) for filemeta in res["hits"]["hits"]]

    def search_all_by_name(self, query, _from=0, _size=1000):
        # TODO: Deprecated. Make Search class?
        body = {
                "query": { 
                    "fuzzy_like_this": { 
                        "like_text": query,
                        "fields": [ "name", "title", "identifier", "description", "filename"],
                    }
                },
            }
        res = self.es.search(index=self.es_index, body=body, from_=_from, size=_size)
        items = []
        for item in res["hits"]["hits"]:
            x = {}
            x["id"] = item["_id"]
            x["type"] = item["_type"]
            if item["_source"].has_key("name"):
                x["name"] = item["_source"]["name"]
            else:
                x["name"] = item["_source"]["filename"]
            items.append(x)
        return items

    def get_tag_dict(self):
        # TODO: Deprecated
        cnt, tags = self.list_tags()
        d = {}
        for tag in tags:
            d[tag["name"]] = tag
        return d
