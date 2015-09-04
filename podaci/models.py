from django.db import models

import os
import shutil
import magic
import zipfile
import StringIO

# as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from settings.settings import AUTH_USER_MODEL
from settings.settings import PODACI_FS_ROOT

from podaci.util import sha256sum
from podaci.search import index_file

# More depth means deeper nesting, which increases lookup speed but makes
# backups exponentially harder
# More length means more directories per nest level, which reduces lookup
# speed but may provide good balance towards depth.
# DEPTH=3, LENGTH=2 is a reasonable default.
# WARNING: NEVER CHANGE THIS IN LIVE SYSTEMS AS ALL WILL BE LOST.
HASH_DIRS_DEPTH = 3
HASH_DIRS_LENGTH = 2


class AuthenticationError(Exception):

    def __str__(self):
        return "Access denied"


class FileNotFound(Exception):

    def __str__(self):
        return "[File not found]"


class ZipSetMixin(object):

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
                zf.write(f.local_path, f.filename)
        zstr.seek(0)
        return zstr


class PodaciTag(ZipSetMixin, models.Model):
    name                = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def to_json(self):
        fields = ("id", "name", "icon")
        out = dict([(x, getattr(self, x)) for x in fields])
        files = self.list_files()
        out["file_count"] = files.count()
        out["files"] = [x.id for x in files]
        return out

    def list_files(self):
        """Return a list of existing files"""
        # TODO: Limit this to only include files the user can see.
        return self.files.all()

    def has_files(self):
        """Return the number of files associated with this tag."""
        return self.files.count() > 0


class PodaciFile(models.Model):
    filename            = models.CharField(max_length=256)
    date_added          = models.DateTimeField(auto_now_add=True)
    public_read         = models.BooleanField(default=False)
    staff_read          = models.BooleanField(default=False)

    allowed_users_read  = models.ManyToManyField(AUTH_USER_MODEL,
        related_name='%(class)s_files_perm_read')
    allowed_users_write = models.ManyToManyField(AUTH_USER_MODEL,
        related_name='%(class)s_files_perm_write')

    schema_version      = models.IntegerField(default=3)
    title               = models.CharField(max_length=300, blank=True, null=True)
    created_by          = models.ForeignKey(AUTH_USER_MODEL,
                            related_name='created_files', blank=True, null=True)
    url                 = models.URLField(blank=True)
    sha256              = models.CharField(max_length=65)
    size                = models.IntegerField(default=0)
    tags                = models.ManyToManyField(PodaciTag,
                            related_name='files')
    mimetype            = models.CharField(max_length=65)
    description         = models.TextField(blank=True)
    is_entity_extracted = models.BooleanField(default=False)

    def log(self, message, user):
        """Add a log entry."""
        cl = PodaciFileChangelog(ref=self, user=user, description=message)
        cl.save()

    def add_user(self, user, write=False):
        """ Give a user permissions on the object. """
        if not user: return
        if user not in self.allowed_users_read.all():
            self.allowed_users_read.add(user.id)
        if write and user not in self.allowed_users_write.all():
            self.allowed_users_write.add(user.id)
        self.log("Added user '%s' [%d] (write=%s)"
                 % (user.email, user.id, write), user)

    def remove_user(self, user):
        """ Revoke user permissions. """
        if not user:
            return
        try:
            self.allowed_users_read.remove(user)
            self.allowed_users_write.remove(user)
            self.log("Removed user '%s' [%d]" % (user.email, user.id), user)
        except ValueError:
            pass

    def make_public(self, user=None):
        """Allow public reads."""
        self.public_read = True
        self.save()
        if user:
            self.log("Made file public.", user)

    def make_private(self, user=None):
        """Disallow public reads."""
        self.public_read = False
        self.save()
        if user:
            self.log("Made file private.", user)

    def allow_staff(self, user=None):
        """Allow all staff members to access (read/write)"""
        self.staff_read = True
        self.save()
        if user:
            self.log("Made file accessible to all staff.", user)

    def disallow_staff(self, user=None):
        """Disallow staff to access"""
        self.staff_read = False
        self.save()
        if user:
            self.log("Made file inaccessible to staff.", user)

    def has_permission(self, user):
        """Check if a given user has read permission."""
        if not user and not self.pk:
            return True
        if not user:
            return False
        if user.is_superuser:
            return True
        if self.public_read:
            return True
        if self.staff_read and user.is_staff:
            return True
        if user in self.allowed_users_read.all():
            return True
        return False

    def has_write_permission(self, user):
        """Check if a given user has write permission."""
        if not user and not self.pk:
            return True
        if not user:
            return False
        if user.is_superuser:
            return True
        if self.staff_read and user.is_staff:
            return True
        if user in self.allowed_users_write.all():
            return True
        return False

    def to_json(self):
        fields = ("id", "schema_version", "title", "filename", "url", "sha256",
                  "size", "mimetype", "description", "date_added",
                  "public_read", "staff_read")
        out = dict([(x, getattr(self, x)) for x in fields])
        out["tags"] = [x.name for x in self.tags.all()]
        if self.created_by is not None:
            out["created_by"] = self.created_by.id
        out["allowed_users_read"] = [x.id for x in self.allowed_users_read.all()]
        out["allowed_users_write"] = [x.id for x in self.allowed_users_write.all()]
        return out

    def get_filehandle(self, user):
        """ Get a file handle to the file itself. """
        if not self.has_permission(user):
            raise AuthenticationError("User %s has no access to file %s"
                                      % (user, self.id))
        return open(self.local_path)

    @property
    def local_path(self):
        """Return the resident location of the file."""
        if self.sha256 is None or not len(self.sha256.strip()):
            raise Exception("File hash missing")
        if self.filename is None or not len(self.filename.strip()):
            raise Exception("Filename missing")

        hashfragment = self.sha256[:HASH_DIRS_DEPTH*HASH_DIRS_LENGTH]
        bytesets = [iter(hashfragment)]*HASH_DIRS_LENGTH
        dirnames = map(lambda *x: "".join(zip(*x)[0]), *bytesets)
        directory = os.path.join(PODACI_FS_ROOT, *dirnames)

        try:
            os.makedirs(directory)
        except:
            pass
        return os.path.join(directory, self.filename)

    @classmethod
    def create_from_filehandle(cls, fh, filename=None, user=None):
        """Given a file handle, create a file."""
        if filename is None and hasattr(fh, 'name'):
            filename = fh.name
        if filename is None:
            filename = "Untitled file"
        obj = cls()
        obj.title = filename
        obj.filename = filename
        obj.sha256 = sha256sum(fh)
        obj.created_by = user
        obj.mimetype = magic.Magic(mime=True).from_buffer(fh.read(100))

        fh.seek(0)
        with open(obj.local_path, 'w') as destfh:
            shutil.copyfileobj(fh, destfh)

        obj.save()
        if user:
            obj.add_user(user, write=True)

        obj.update()
        return obj

    @classmethod
    def create_from_path(cls, filename, filename_override=None, user=None):
        """Given a file path, create a file."""
        if not os.path.isfile(filename):
            raise ValueError("File does not exist")
        fn = filename_override or os.path.basename(filename)
        with open(filename, 'r') as fh:
            return cls.create_from_filehandle(fh, filename=fn, user=user)

    def update(self):
        if os.path.isfile(self.local_path):
            self.size = os.stat(self.local_path).st_size
        index_file(self)
        self.save()

    def exists_by_hash(self, sha):
        return PodaciFile.objects.filter(sha256=sha).count() > 0

    def exists_by_url(self, url):
        return PodaciFile.objects.filter(url=url).count() > 0

    def delete(self):
        """Delete a file. Make sure you're sure."""
        if not self.id:
            raise ValueError("No file specified")
        if self.filename:
            try:
                os.unlink(self.local_path)
            except OSError:
                return False
        return True

    def tag_add(self, tag):
        if tag not in self.tags.all():
            self.tags.add(tag)

    def tag_remove(self, tag):
        self.tags.remove(tag)

    @property
    def thumbnail(self):
        # if os.path.isfile(self.thumbnail_real_location(160, 160)):
        #     return self.thumbnail_uri(160, 160)
        return "/static/img/podaci/file.png"
    #
    # def gen_thumbnail(self, width=680, height=460):
    #     """Return a thumbnail of a file."""
    #     # Todo: Perhaps this belongs elsewhere?
    #     if self.mimetype:
    #         basetype, subtype = self.mimetype.split("/")
    #     else:
    #         return False
    #
    #     if basetype == "image":
    #         return self.thumbnail_imagemagick(width, height)
    #     elif basetype == "application":
    #         if subtype == "pdf":
    #             return self.thumbnail_imagemagick(width, height)
    #
    #         return False
    #     return False
    #
    # def thumbnail_real_location(self, width, height):
    #     return "/home/smari/Projects/OCCRP/id2/static/thumbnails/%s" % (self.thumbnail_filename(width, height))
    #
    # def thumbnail_uri(self, width, height):
    #     return "/static/thumbnails/%s" % (self.thumbnail_filename(width, height))
    #
    # def thumbnail_filename(self, width, height):
    #     return "%s_%dx%d.png" % (self.sha256, width, height)
    #
    # def thumbnail_imagemagick(self, width, height):
    #     try:
    #         import subprocess
    #         params = ['convert',
    #                   '-density', '300',
    #                   '-resize', '%dx%d' % (width, height),
    #                   self.local_path,
    #                   self.thumbnail_real_location(width, height)]
    #         subprocess.check_call(params)
    #         return self.thumbnail_uri(width, height)
    #     except:
    #         return False


class PodaciCollection(ZipSetMixin, models.Model):
    name                = models.CharField(max_length=300)
    owner               = models.ForeignKey(AUTH_USER_MODEL,
                            related_name='collections', default=1)
    description         = models.TextField(blank=True)
    files               = models.ManyToManyField(PodaciFile,
                            related_name='collections')
    shared_with         = models.ManyToManyField(AUTH_USER_MODEL)

    class Meta:
        unique_together = (('name', 'owner'),)
        ordering = ('name',)

    def file_add(self, cfile):
        if cfile not in self.files.all():
            self.files.add(cfile)

    def file_remove(self, cfile):
        self.files.remove(cfile)

    def tag_add(self, parenttag):
        """ tagging a collection simply tags all files within """
        for f in self.files.all():
            f.tag_add(parenttag)

    def tag_remove(self, parenttag):
        """ same with removing a tag """
        for f in self.files.all():
            f.tag_remove(parenttag)

    def to_json(self):
        fields = ("id", "name", "description", "owner")
        out = dict([(x, getattr(self, x)) for x in fields])
        out["files"] = [x.id for x in self.files.all()]
        return out

    def list_files(self):
        """Return a list of existing files"""
        # TODO: Limit this to only include files the user can see.
        return self.files.all()

    def has_files(self):
        """Return the number of files associated with this tag."""
        return self.files.count() > 0


class PodaciFileChangelog(models.Model):
    ref                 = models.ForeignKey(PodaciFile, related_name="logs")
    user                = models.ForeignKey(AUTH_USER_MODEL)
    timestamp           = models.DateTimeField(auto_now_add=True)
    description         = models.CharField(max_length=200)
