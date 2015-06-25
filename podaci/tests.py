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
            if tag.has_permission(self.fs.user):
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


class PodaciFileSystemTest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_filesystem_status(self):
        # status = self.fs.status()
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


class PodaciTagTest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_has_files(self):
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        t = PodaciTag(name="thistest")
        t.save()
        self.assertEqual(t.has_files(), 0)
        f.tags.add(t)
        self.assertEqual(t.has_files(), 1)
        f.tags.remove(t)
        self.assertEqual(t.has_files(), 0)
        t.delete()
        f.delete()


class PodaciWebInterfaceTest(UserTestCase):
    def req_as_staff(self, urlname, get=False, args={}, dset={}):
        client = TestClient()
        client.login_user(self.staff_user)
        url = reverse(urlname, kwargs=args)
        if get:
            response = client.get(url, dset)
        else:
            response = client.post(url, dset)
        return response

    def test_podaci_info_home(self):
        res = self.req_as_staff('podaci_info_home')

    def test_podaci_info_help(self):
        res = self.req_as_staff('podaci_info_help', get=True)

    def test_podaci_search(self):
        res = self.req_as_staff('podaci_search')

    def test_podaci_search_mention(self):
        res = self.req_as_staff('podaci_search_mention')

    def test_podaci_info_status(self):
        res = self.req_as_staff('podaci_info_status')

    def test_podaci_info_statistics(self):
        res = self.req_as_staff('podaci_info_statistics')

    def test_podaci_files_create_success(self):
        with open("requirements.txt") as fp:
            res = self.req_as_staff('podaci_files_create', 
                dset={"files[]": [fp]})
        data = json.loads(res.content)
        self.assertEqual(data["filename"], "requirements.txt")
        self.assertIn(self.staff_user.id, data["allowed_users_read"])
        self.assertNotIn(self.admin_user.id, data["allowed_users_read"])
        self.assertEqual(data["public_read"], False)
        self.assertEqual(data["mimetype"], "text/plain")
        # Clean up after ourselves...
        f = PodaciFile.objects.get(id=data["id"])
        f.delete()

    #def test_podaci_files_create_fail(self):
    #    # Next, let's try failing:
    #    pass

    def test_podaci_files_note_add(self):
        pass # res = self.req_as_staff('podaci_files_note_add')

    def test_podaci_files_note_delete(self):
        pass # res = self.req_as_staff('podaci_files_note_delete')

    def test_podaci_files_note_update(self):
        pass # res = self.req_as_staff('podaci_files_note_update')

    def test_podaci_files_delete(self):
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        res = self.req_as_staff('podaci_files_delete', 
                                args={"id": f.id})
        data = json.loads(res.content)
        self.assertEqual(data["deleted"], True)
        self.assertEqual(data["id"], str(f.id))

    def test_podaci_files_upload(self):
        pass # res = self.req_as_staff('podaci_files_upload')

    def test_podaci_files_download(self):
        pass # res = self.req_as_staff('podaci_files_download')

    def test_podaci_files_details(self):
        f = PodaciFile()
        f.create_from_path("requirements.txt")
        res = self.req_as_staff('podaci_files_details', 
                                args={"id": f.id})
        data = json.loads(res.content)
        self.assertIn("file", data)
        self.assertIn("tags", data)
        self.assertIn("notes", data)
        self.assertIn("users", data)
        f.delete()

    def test_podaci_tags_create(self):
        pass # res = self.req_as_staff('podaci_tags_create')

    def test_podaci_tags_list(self):
        pass # res = self.req_as_staff('podaci_tags_list')

    def test_podaci_tags_delete(self):
        pass # res = self.req_as_staff('podaci_tags_delete')

    def test_podaci_tags_upload(self):
        pass # res = self.req_as_staff('podaci_tags_upload')

    def test_podaci_tags_zip_tag(self):
        pass # res = self.req_as_staff('podaci_tags_zip')

    def test_podaci_tags_zip_selection(self):
        pass # res = self.req_as_staff('podaci_tags_zip')

    def test_podaci_tags_details(self):
        pass # res = self.req_as_staff('podaci_tags_details')

