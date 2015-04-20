from django.test import TestCase
from core.tests import UserTestCase
from core.testclient import TestClient
from settings.settings import *
from django.core.urlresolvers import reverse
from podaci.filesystem import *
import os, shutil
import time
import json

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
        ## Test adding a tag to a file
        ## Also tests if a tag has files
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
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=self.admin_user)

        f = File(self.fs)
        f.create_from_path("requirements.txt")
        f.make_public()
        self.assertEqual(f.has_permission(self.anonymous_user), True)
        fh = f.get_filehandle()
        self.assertEqual(type(fh), file)
        f.make_private()
        self.assertEqual(f.has_permission(self.anonymous_user), False)
        f.delete(True)

    def test_logged_in_access(self):
        ## Verify that a logged in user cannot access a non-public file
        ## they have no permission for
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=self.admin_user)

        f = File(self.fs)
        f.create_from_path("requirements.txt")
        f.make_public()
        self.assertEqual(f.has_permission(self.normal_user), True)
        self.assertEqual(f.has_write_permission(self.normal_user), False)
        f.make_private()
        self.assertEqual(f.has_permission(self.normal_user), False)
        self.assertEqual(f.has_write_permission(self.normal_user), False)
        f.delete(True)

    def test_logged_in_with_direct_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have explicit access to
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=self.admin_user)

        f = File(self.fs)
        f.create_from_path("requirements.txt")
        f.make_private()
        f.add_user(self.normal_user)
        self.assertEqual(f.has_permission(self.normal_user), True)
        f.delete(True)

    def test_logged_in_with_indirect_access(self):
        ## Verify that a logged in user can access a non-public file they
        ## have access to through a tag they are allowed on
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari"))
        pass

    def text_staff_access(self):
        ## Verify that staff can access staff-allowed files.
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, 
                             user=Strawman("smari", admin=True))
        f = File(self.fs)
        f.create_from_path("requirements.txt")
        f.allow_staff()
        self.assertEqual(f.has_permission(self.staff_user), True)
        self.assertEqual(f.has_write_permission(self.staff_user), True)
        f.disallow_staff()
        self.assertEqual(f.has_permission(self.staff_user), False)
        self.assertEqual(f.has_write_permission(self.staff_user), False)
        f.delete(True)

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

    def test_filesystem_status(self):
        status = self.fs.status()

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
        f.delete(sure=True)

    def test_get_file(self):
        pass # f = File(self.fs)

    def test_notes(self):
        f = File(self.fs)
        f.create_from_path("requirements.txt")
        f.note_add("This is a note")
        f.note_add("This is another note")

        self.assertEqual(len(f.note_list()), 2)
        for note in f.note_list()[:]:
            f.note_delete(note["id"])

        self.assertEqual(len(f.note_list()), 0)
        f.delete(sure=True)


class PodaciTagTest(TestCase):
    def setUp(self):
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)
        self.fs = FileSystem(PODACI_SERVERS, PODACI_ES_INDEX, PODACI_FS_ROOT, user=Strawman("smari"))

    def tearDown(self):
        shutil.rmtree(PODACI_FS_ROOT)

    def test_has_files(self):
        f = File(self.fs)
        f.create_from_path("requirements.txt")
        t = Tag(self.fs)
        t.create("thistest")
        self.assertEqual(t.has_files(), 0)
        f.add_tag(t)
        time.sleep(1)
        self.assertEqual(t.has_files(), 1)
        f.remove_tag(t)
        time.sleep(1)
        self.assertEqual(t.has_files(), 0)
        t.delete(sure=True)
        f.delete(sure=True)


class PodaciWebInterfaceTest(UserTestCase):
    def setUp(self):
        super(PodaciWebInterfaceTest, self).setUp()
        self.fs = FileSystem(PODACI_SERVERS, 
                             PODACI_ES_INDEX, 
                             PODACI_FS_ROOT, 
                             user=self.staff_user)

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
        self.assertEqual(len(data), 3)
        self.assertEqual(data[1]["filename"], "requirements.txt")
        self.assertIn(self.staff_user.id, data[1]["allowed_users"])
        self.assertNotIn(self.admin_user.id, data[1]["allowed_users"])
        self.assertEqual(data[1]["public_read"], False)
        self.assertEqual(data[1]["mimetype"], "text/plain")
        # Clean up after ourselves...
        f = File(self.fs)
        f.load(data[0])
        f.delete(True)

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
        f = File(self.fs)
        f.create_from_path("requirements.txt")
        res = self.req_as_staff('podaci_files_delete', 
                                args={"id": f.id})
        data = json.loads(res.content)
        self.assertEqual(data["deleted"], True)
        self.assertEqual(data["id"], f.id)

    def test_podaci_files_upload(self):
        pass # res = self.req_as_staff('podaci_files_upload')

    def test_podaci_files_download(self):
        pass # res = self.req_as_staff('podaci_files_download')

    def test_podaci_files_details(self):
        f = File(self.fs)
        f.create_from_path("requirements.txt")
        res = self.req_as_staff('podaci_files_details', 
                                args={"id": f.id})
        data = json.loads(res.content)
        self.assertIn("file", data)
        self.assertIn("tags", data)
        self.assertIn("notes", data)
        self.assertIn("users", data)
        f.delete(True)

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

