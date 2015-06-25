from django.db import models
from django.utils.translation import ugettext_lazy as _

import hashlib
import os, os.path, shutil, sys
import magic
import zipfile
import StringIO
import logging
from datetime import datetime
from uuid import uuid4

from settings.settings import AUTH_USER_MODEL # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from settings.settings import PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT

# More depth means deeper nesting, which increases lookup speed but makes 
# backups exponentially harder
# More length means more directories per nest level, which reduces lookup
# speed but may provide good balance towards depth. 
# DEPTH=3, LENGTH=2 is a reasonable default.
# WARNING: NEVER CHANGE THIS IN LIVE SYSTEMS AS ALL WILL BE LOST.
HASH_DIRS_DEPTH = 3
HASH_DIRS_LENGTH = 2


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


class PodaciMetadata(models.Model):
    name                = models.CharField(max_length=200)
    date_added          = models.DateTimeField(auto_now_add=True)
    public_read         = models.BooleanField(default=False)
    staff_read          = models.BooleanField(default=False)
    allowed_users_read  = models.ManyToManyField(AUTH_USER_MODEL, 
        related_name='%(class)s_files_perm_read')
    allowed_users_write = models.ManyToManyField(AUTH_USER_MODEL, 
        related_name='%(class)s_files_perm_write')

    class Meta:
        abstract = True

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        for field_name in self._meta.get_all_field_names():
            try:
                value = getattr(self, field_name)
            except:
                value = None
            yield (field_name, value)

    #def __init__(self, *args, **kwargs):
    #    user = kwargs.pop('user', None)
    #    super(models.Model, self).__init__(*args, **kwargs)
    #    #if not self.has_permission(user):
    #    #    raise AuthenticationError("User %s has no access to tag %s" 
    #    #        % (user, self.pk))

    def log(self, message, user):
        """Add a log entry."""
        if self.CHANGELOG_CLASS:
            # TODO: Make this smarter.
            cl = globals()[self.CHANGELOG_CLASS]()
            cl.ref = self
            cl.user = user
            cl.message = message
            cl.save()

    def note_add(self, text, user):
        """Add a log entry."""
        if self.NOTE_CLASS:
            # TODO: Make this smarter.
            cl = globals()[self.NOTE_CLASS]()
            cl.ref = self
            cl.user = user
            cl.text = text
            cl.save()

        self.log("Added note", user)

    def note_list(self):
        if self.NOTE_CLASS:
            return globals()[self.NOTE_CLASS].objects.filter(ref=self)
        return []

    def note_delete(self, nid):
        if self.NOTE_CLASS:
            note = globals()[self.NOTE_CLASS].objects.get(id=nid)
            note.delete()

    def details_string(self):
        """
           Return a formatted details string that describes the object's 
           permissions.
        """
        s = "%s%s %3dU %3dW %3dN" % (
            ["-","P"][self.public_read], 
            ["-","S"][self.staff_read], 
            self.allowed_users_read.count(), 
            self.allowed_users_write.count(), 
            self.notes.count())
        if self.DOCTYPE == "tag":
            s += " %4dF" % (self.list_files().count())
        return s

    def to_json(self):
        """Get a JSON blob containing the ID and the object's metadata."""
        return {"id": self.id}

    def add_user(self, user, write=False):
        """Give a user permissions on the object."""
        if not user: return
        if user not in self.allowed_users_read.all():
            self.allowed_users_read.add(user.id)
        if write and user not in self.allowed_users_write.all():
            self.allowed_users_write.add(user.id)
        self.log("Added user '%s' [%d] (write=%s)" 
                 % (user.email, user.id, write), user)

    def remove_user(self, user):
        """Revoke user permissions."""
        if not user: return
        try:
            self.allowed_users_read.remove(user)
            self.allowed_users_write.remove(user)
            self.log("Removed user '%s' [%d]" % (user.email, user.id), user)
        except ValueError:
            pass

    def make_public(self, user):
        """Allow public reads."""
        self.public_read = True
        self.save()
        self.log("Made file public.", user)

    def make_private(self, user):
        """Disallow public reads."""
        self.public_read = False
        self.save()
        self.log("Made file private.", user)

    def allow_staff(self, user):
        """Allow all staff members to access (read/write)"""
        self.staff_read = True
        self.save()
        self.log("Made file accessible to all staff.", user)

    def disallow_staff(self, user):
        """Disallow staff to access"""
        self.staff_read = False
        self.save()
        self.log("Made file inaccessible to staff.", user)

    def has_permission(self, user):
        """Check if a given user has read permission."""
        if not user and not self.pk: return True
        if not user: return False
        if user.is_superuser: return True
        if self.public_read: return True
        if self.staff_read and user.is_staff: return True
        if user in self.allowed_users_read.all(): return True
        if self.DOCTYPE == "file":
            for t in self.tags.all():
                tag = Tag.objects.get(id=t)
                if tag.has_permission(user):
                    return True
        return False

    def has_write_permission(self, user):
        """Check if a given user has write permission."""
        if not user and not self.pk: return True
        if not user: return False
        if user.is_superuser: return True
        if self.staff_read and user.is_staff: return True
        if user in self.allowed_users_write.all(): return True
        if self.DOCTYPE == "file":
            for t in self.tags.all():
                if t.has_write_permission(user):
                    return True
        return False


class PodaciTag(PodaciMetadata):
    parents             = models.ManyToManyField('PodaciTag', 
                            related_name='children')
    icon                = models.CharField(max_length=100)

    DOCTYPE             = 'tag'
    CHANGELOG_CLASS     = 'PodaciTagChangelog'
    NOTE_CLASS          = None

    def __unicode__(self):
        if not self.id: return "[Uninitialized tag object]"
        return "[Tag %s] %s" % (self.id, self.name)

    def __str__(self):
        return self.__unicode__()

    def to_json(self):
        fields = ("id", "parents", "icon",
                  "name", "date_added", "public_read", "staff_read")
        out = dict([(x, getattr(self, x)) for x in fields])
        out["tags"] = [x.id for x in self.tags.all()]
        out["allowed_users_read"] = [x.id for x in self.allowed_users_read.all()]
        out["allowed_users_write"] = [x.id for x in self.allowed_users_write.all()]
        return out

    def parent_add(self, parenttag):
        """Add a parent tag."""
        if parenttag not in self.parents.objects.all():
            self.parents.add(parenttag)

    def parent_remove(self, parenttag):
        """Disown a parent tag."""
        self.parents.remove(parenttag)

    def child_add(self, childtag):
        """Add a child tag."""
        if self not in childtag.parents.objects.all():
            childtag.parents.add(self)

    def child_remove(self, childtag):
        """Disown a child tag."""
        childtag.parents.remove(self)

    def list_files(self):
        """Return a list of existing files"""
        # TODO: Limit this to only include files the user can see.
        return self.files.all()

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
        totalsize = sum([x.size for x in files])
        if totalsize > _50MB:
            return False

        zstr = StringIO.StringIO()
        with zipfile.ZipFile(zstr, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f.resident_location(), f.filename)
        zstr.seek(0)
        return zstr

    def has_files(self):
        """Return the number of files associated with this tag."""
        return self.files.count() > 0



class PodaciFile(PodaciMetadata):
    schema_version      = models.IntegerField(default=3)
    title               = models.CharField(max_length=300)
    created_by          = models.ForeignKey(AUTH_USER_MODEL, 
                            related_name='created_files', blank=True, null=True)
    is_resident         = models.BooleanField(default=True)
    filename            = models.CharField(max_length=256, blank=True)
    url                 = models.URLField(blank=True)
    sha256              = models.CharField(max_length=65)
    size                = models.IntegerField(default=0)
    tags                = models.ManyToManyField(PodaciTag, 
                            related_name='files')
    mimetype            = models.CharField(max_length=65)
    description         = models.TextField(blank=True)
    is_indexed          = models.BooleanField(default=False)
    is_entity_extracted = models.BooleanField(default=False)

    DOCTYPE             = 'file'
    CHANGELOG_CLASS     = 'PodaciFileChangelog'
    NOTE_CLASS          = 'PodaciFileNote'

    def to_json(self):
        fields = ("id", "schema_version", "title", "created_by", "is_resident",
                  "filename", "url", "sha256", "size", "mimetype", 
                  "description", "is_indexed", "is_entity_extracted",
                  "name", "date_added", "public_read", "staff_read")
        out = dict([(x, getattr(self, x)) for x in fields])
        out["tags"] = [x.id for x in self.tags.all()]
        out["allowed_users_read"] = [x.id for x in self.allowed_users_read.all()]
        out["allowed_users_write"] = [x.id for x in self.allowed_users_write.all()]
        return out

    def get_filehandle(self, user):
        """Get a file handle to the file itself."""
        if not self.has_permission(user):
            raise AuthenticationError("User %s has no access to file %s" 
                % (user, self.id))
        if self.is_resident:
            return open(self.resident_location())
        else:
            return urllib2.urlopen(self.url)

    def resident_location(self):
        """Return the resident location of the file."""
        if self.sha256 == "": raise Exception("File hash missing")
        if self.filename == "": raise Exception("Filename missing")
        hashfragment = self.sha256[:HASH_DIRS_DEPTH*HASH_DIRS_LENGTH]
        bytesets = [iter(hashfragment)]*HASH_DIRS_LENGTH
        dirnames = map(lambda *x: "".join(zip(*x)[0]), *bytesets)
        directory = os.path.join(PODACI_FS_ROOT, *dirnames)
        try:
            os.makedirs(directory)
        except os.error:
            pass
        return os.path.join(directory, self.filename)

    def create_from_filehandle(self, fh, filename=None, user=None):
        """Given a file handle, create a file."""
        if not filename:
            filename = fh.name
        if not filename:
            filename = "Untitled file"
        self.filename = filename
        self.sha256 = sha256sum(fh)
        self.mimetype = magic.Magic(mime=True).from_buffer(fh.read(100))

        fh.seek(0)
        f = open(self.resident_location(), "w+")
        f.write(fh.read())
        f.close()

        self.size = os.stat(self.resident_location()).st_size
        self.save()
        if user:
            self.add_user(user, write=True)

        return self.id, self, True

    def create_from_path(self, filename, filename_override=None, user=None):
        """Given a file path, create a file."""
        if not os.path.isfile(filename): raise ValueError("File does not exist")
        self.filename = os.path.split(filename)[-1]
        if filename_override:
            self.filename = filename_override
        self.sha256 = sha256sum(filename)
        self.mimetype = magic.Magic(mime=True).from_file(filename)

        shutil.copy(filename, self.resident_location())
        self.size = os.stat(self.resident_location()).st_size
        self.save()

        if user:
            self.add_user(user, write=True)

        return self.id, self, True

    def create_from_url(self, url, make_resident=False, user=None):
        """Given a URL, create a file. Optionally, make the file resident."""
        self.url = url
        self.is_resident = False

        self.save()

        if user:
            self.add_user(user, write=True)

        if make_resident:
            self._make_resident()

        return self.id, self, True

    def exists_by_hash(self, sha):
        return PodaciFile.objects.filter(sha256=sha).count() > 0

    def exists_by_url(self, url):
        return PodaciFile.objects.filter(url=url).count() > 0

    def _make_resident(self, buf=None):
        """Makes a resident copy of an URL-based file entry."""
        raise NotImplementedError()
        self.is_resident = True

    def delete(self):
        """Delete a file. Make sure you're sure."""
        if not self.id: raise ValueError("No file specified")
        if self.filename:
            try:
                os.unlink(self.resident_location())
            except OSError:
                pass
        super(PodaciMetadata, self).delete()
        return True

    def get_thumbnail(self, width=680, height=460):
        """Return a thumbnail of a file."""
        # Todo: Perhaps this belongs elsewhere?
        if self.mimetype:
            basetype, subtype = self.mimetype.split("/")
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


class PodaciTriples(models.Model):
    class Meta:
        abstract = True

    key                 = models.CharField(max_length=200)
    value               = models.TextField()

class PodaciFileTriples(PodaciTriples):
    ref                 = models.ForeignKey(PodaciFile, related_name="metadata")

class PodaciChangelog(models.Model):
    class Meta:
        abstract = True

    user                = models.ForeignKey(AUTH_USER_MODEL)
    timestamp           = models.DateTimeField(auto_now_add=True)
    description         = models.CharField(max_length=200)

class PodaciTagChangelog(PodaciChangelog):
    ref                 = models.ForeignKey(PodaciTag, related_name="logs")

class PodaciFileChangelog(PodaciChangelog):
    ref                 = models.ForeignKey(PodaciFile, related_name="logs")

class PodaciFileNote(models.Model):
    user                = models.ForeignKey(AUTH_USER_MODEL)
    timestamp           = models.DateTimeField(auto_now_add=True)
    ref                 = models.ForeignKey(PodaciFile, related_name="notes")
    description         = models.TextField()
