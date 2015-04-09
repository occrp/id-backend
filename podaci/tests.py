from django.contrib.auth.models import AnonymousUser#, User
from django.test import TestCase
from settings.settings import *
from podaci.filesystem import *
import os, shutil

class Strawman:
    def __init__(self, email, admin=False):
        self.id = 1
        self.email = email
        self.is_superuser = admin


class PodaciAPITest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari"))

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_create_and_delete_file(self):
        ## Create a file!
        f = File(self.fs)
        f.create_from_path("requirements.txt")
        self.assertEqual(f.meta["filename"], "requirements.txt")
        self.assertEqual(f.exists, True)
        f.delete(sure=True)
        self.assertEqual(f.exists, False)

    def test_add_tag(self):
        ## Add tag
        f = File(self.fs)
        f.create_from_path("requirements.txt")
        t = Tag(self.fs)
        t.create("tech")
        f.add_tag(t)
        self.assertEqual(f.meta["tags"], [t.id])
        f.delete(sure=True)
        t.delete(sure=True)

    def test_list_tags(self):
        count, tags = self.fs.list_tags()
        for tag in tags:
            if tag.has_permission(self.fs.user):
                tag.list_files()

    def test_find_nonexistant_file(self):
        ## Check for non-existent file by hash:
        self.assertEqual(File(self.fs).exists_by_hash("not a real hash"), False)

    def test_search_files(self):
        ## Search for files...
        self.fs.search_files({"query":{"term":{"public_read":False}}})


class PodaciPermissionTest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_anonymous_with_access(self):
        ## Verify that an anonymous user can access a public file
        u = AnonymousUser()
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari"))
        

    def test_anonymous_without_access(self):
        ## Verify that an anonymous user can't access a non-public file
        u = AnonymousUser()
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari"))
        pass

    def test_logged_in_without_access(self):
        ## Verify that a logged in user cannot access a non-public file
        ## they have no permission for
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari"))

        pass

    def test_logged_in_with_direct_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have explicit access to
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari"))

        pass

    def test_logged_in_with_indirect_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have access to through a tag they are allowed on
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari"))

        pass

    def test_admin_access(self):
        ## Verify that an admin user always has access
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari", admin=True))

        pass


class PodaciFileSystemTest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, user=Strawman("smari"))

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

class PodaciFileTest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, user=Strawman("smari"))

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_create_file_from_filehandle(self):
        f = File(self.fs)
        fh = StringIO.StringIO()
        fh.write("Test file")
        fh.seek(0)
        f.create_from_filehandle(fh, "test.txt")
        self.assertEqual(f.exists, True)

    def test_get_file(self):
        f = File(self.fs)
