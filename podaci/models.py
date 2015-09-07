from django.db import models

import os
import shutil
import magic

# as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from settings.settings import AUTH_USER_MODEL
from settings.settings import PODACI_FS_ROOT

from podaci.util import sha256sum
from podaci.search import index_file
from core.mixins import NotificationMixin

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


class PodaciTag(NotificationMixin, models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self)

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


class PodaciFile(NotificationMixin, models.Model):
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

    def __unicode__(self):
        return self.title or self.filename

    def notify(self, message, user, action, urlname='podaci_file_detail',
               params=None):
        """ Create a notification about a thing. """
        pass
        # from id.models import Notification
        # n = Notification()
        # stream = 'id:podaci:file:%s' % self.id
        # n.create(user, stream, message, urlname=urlname,
        #          params=params if params is not None else {'pk': self.id},
        #          action=action)
        # n.save()

    def add_user(self, user, write=False, notify=True):
        """ Give a user permissions on the object. """
        if not user: return
        if user not in self.allowed_users_read.all():
            self.allowed_users_read.add(user.id)
        if write and user not in self.allowed_users_write.all():
            self.allowed_users_write.add(user.id)
        if notify:
            self.notify("Added user '%s' to file: %s" % (user, self),
                        user, "share")

    def remove_user(self, user):
        """ Revoke user permissions. """
        if not user:
            return
        try:
            self.allowed_users_read.remove(user)
            self.allowed_users_write.remove(user)
            self.notify("Removed user '%s' from file: %s" % (user, self),
                        user, "share")
        except ValueError:
            pass

    def make_public(self, user=None):
        """Allow public reads."""
        self.public_read = True
        self.save()
        if user:
            self.notify("Made file '%s' public." % self, user, "edit")

    def make_private(self, user=None):
        """Disallow public reads."""
        self.public_read = False
        self.save()
        if user:
            self.notify("Made file '%s' private." % self, user, "edit")

    def allow_staff(self, user=None):
        """Allow all staff members to access (read/write)"""
        self.staff_read = True
        self.save()
        if user:
            self.notify("Made file '%s' accessible to staff." % self,
                        user, "share")

    def disallow_staff(self, user=None):
        """Disallow staff to access"""
        self.staff_read = False
        self.save()
        if user:
            self.notify("Made file '%s' inaccessible to staff." % self,
                        user, "share")

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
        out["allowed_users_read"] = \
            [x.id for x in self.allowed_users_read.all()]
        out["allowed_users_write"] = \
            [x.id for x in self.allowed_users_write.all()]
        out["tickets"] = [x.id for x in self.tickets.all()]
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
    def create_from_filehandle(cls, fh, filename=None, user=None, ticket=None):
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
        if ticket is not None:
            obj.tickets.add(ticket)

        if user:
            obj.add_user(user, write=True, notify=False)
            obj.notify("Created file '%s'." % obj, user, "add")

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


class PodaciCollection(NotificationMixin, models.Model):
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
