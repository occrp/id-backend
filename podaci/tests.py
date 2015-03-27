from django.contrib.auth.models import AnonymousUser#, User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.test import TestCase
from settings.settings import *
from podaci.filesystem import *
import os, shutil

class Strawman:
    def __init__(self, email):
        self.id = 1
        self.email = email


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
        f = self.fs.create_file("requirements.txt")
        self.assertEqual(f.meta["filename"], "requirements.txt")
        f.delete(sure=True)

    def test_add_tag(self):
        ## Add tag
        f = self.fs.create_file("requirements.txt")
        f.add_tag("tech")
        self.assertEqual(f.meta["tags"], ["tech"])

    def test_list_tag(self):
        ## Listing a tag:
        self.fs.list_files("tech")

    def test_find_nonexistant_file(self):
        ## Check for non-existent file by hash:
        self.assertEqual(self.fs.file_exists_by_hash("not a real hash"), False)

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
                             user=u)
        

    def test_anonymous_without_access(self):
        ## Verify that an anonymous user can't access a non-public file
        u = AnonymousUser()
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=u)
        pass

    def test_logged_in_without_access(self):
        ## Verify that a logged in user cannot access a non-public file
        ## they have no permission for
        u = get_user_model(email="testuser@occrp.org")
        u.save()
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=u)

        pass

    def test_logged_in_with_direct_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have explicit access to
        u = get_user_model(email="testuser@occrp.org")
        u.save()
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=u)

        pass

    def test_logged_in_with_indirect_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have access to through a tag they are allowed on
        u = get_user_model(email="testuser@occrp.org")
        u.save()
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=u)

        pass

    def test_admin_access(self):
        ## Verify that an admin user always has access
        u = get_user_model(email="testuser@occrp.org")
        u.is_superuser = True
        u.save()
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=u)

        pass


