from django.test import TestCase
from core.tests import UserTestCase
from core.testclient import TestClient
from settings.settings import *
from django.core.urlresolvers import reverse
from podaci.models import PodaciFile, PodaciTag
import StringIO
import os, shutil
import time
import json


class PodaciAPITest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_create_and_delete_file(self):
        ## Create a file!
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        self.assertEqual(f.filename, "requirements.txt")
        f.delete()

    def test_add_tag(self):
        ## Test adding a tag to a file
        ## Also tests if a tag has files
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        t = PodaciTag()
        t.name = "tech"
        t.save()
        f.tags.add(t)
        self.assertIn(t, f.tags.all())
        f.delete()
        t.delete()

    def test_list_tags(self):
        tags = PodaciTag.objects.all()
        for tag in tags:
            tag.list_files()

    def test_find_nonexistant_file(self):
        ## Check for non-existent file by hash:
        self.assertEqual(PodaciFile().exists_by_hash("not a real hash"), False)

    def test_search_files(self):
        ## Search for files...
        pass #self.fs.search_files({"query":{"term":{"public_read":False}}})


class PodaciPermissionTest(UserTestCase):
    def setUp(self):
        super(PodaciPermissionTest, self).setUp()

        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)
        super(PodaciPermissionTest, self).tearDown()

    def test_anonymous_access(self):
        ## Verify that an anonymous user can access a public file
        ## Verify that an anonymous user can't access a non-public file
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        f.make_public(self.staff_user)
        self.assertEqual(f.has_permission(self.anonymous_user), True)
        fh = f.get_filehandle(self.anonymous_user)
        self.assertEqual(type(fh), file)
        f.make_private(self.staff_user)
        self.assertEqual(f.has_permission(self.anonymous_user), False)
        f.delete()

    def test_logged_in_access(self):
        ## Verify that a logged in user cannot access a non-public file
        ## they have no permission for
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        f.make_public(self.staff_user)
        self.assertEqual(f.has_permission(self.normal_user), True)
        self.assertEqual(f.has_write_permission(self.normal_user), False)
        f.make_private(self.staff_user)
        self.assertEqual(f.has_permission(self.normal_user), False)
        self.assertEqual(f.has_write_permission(self.normal_user), False)
        f.delete()

    def test_logged_in_with_direct_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have explicit access to
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        f.make_private(self.staff_user)
        f.add_user(self.normal_user)
        self.assertEqual(f.has_permission(self.normal_user), True)
        f.delete()

    def test_logged_in_with_indirect_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have access to through a tag they are allowed on
        pass

    def text_staff_access(self):
        ## Verify that staff can access staff-allowed files.
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        f.allow_staff(self.staff_user)
        self.assertEqual(f.has_permission(self.staff_user), True)
        self.assertEqual(f.has_write_permission(self.staff_user), True)
        f.disallow_staff()
        self.assertEqual(f.has_permission(self.staff_user), False)
        self.assertEqual(f.has_write_permission(self.staff_user), False)
        f.delete()

    def test_admin_access(self):
        ## Verify that an admin user always has access
        pass


class PodaciFileTest(UserTestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)
        super(UserTestCase, self).setUp()

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_create_file_from_filehandle(self):
        f = PodaciFile()
        fh = StringIO.StringIO()
        fh.write("Test file")
        fh.seek(0)
        f.create_from_filehandle(fh, "test.txt")
        f.delete()

    def test_get_file(self):
        pass # f = File(self.fs)

    def test_notes(self):
        self.staff_user = self.user_helper('teststaff@occrp.org', is_staff=True)
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        f.note_add("This is a note", self.staff_user)
        f.note_add("This is another note", self.staff_user)

        self.assertEqual(f.note_list().count(), 2)
        f.notes.all().delete()

        self.assertEqual(f.note_list().count(), 0)
        f.delete()
