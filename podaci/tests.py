import StringIO
import os
import shutil

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests import UserTestCase
from settings.settings import PODACI_FS_ROOT
from podaci.models import PodaciFile, PodaciTag


class PodaciModelTest(TestCase):

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


class PodaciAPITest(APITestCase):
    fixtures = ['id/fixtures/initial_data.json']

    def setUp(self):
        super(PodaciAPITest, self).setUp()
        if not os.path.isdir(PODACI_FS_ROOT):
            os.mkdir(PODACI_FS_ROOT)

        user = get_user_model().objects
        self.staff_user = user.get(email='staff@example.com')
        self.admin_user = user.get(email='admin@example.com')
        self.user_user = user.get(email='user@example.com')
        self.other_user = user.get(email='user2@example.com')

        self.file = PodaciFile()
        self.file.create_from_path("requirements.txt", user=self.staff_user)
        self.file.make_private(self.staff_user)
        self.file.add_user(self.user_user)
        self.file.save()

    def tearDown(self):
        super(PodaciAPITest, self).tearDown()
        shutil.rmtree(PODACI_FS_ROOT)

    def test_file_list(self):
        url = reverse('podaci_file_list')
        res = self.client.get(url)
        # is that actually what we want?
        self.assertEqual(res.status_code, 403)
        self.client.force_authenticate(user=self.staff_user)
        res = self.client.get(url)
        # print url, res.content
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)

        self.client.force_authenticate(user=self.other_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 0)

    def test_read_file(self):
        assert self.file.id is not None, self.file
        url = reverse('podaci_file_detail', kwargs={'pk': self.file.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 403)
        self.client.force_authenticate(user=self.staff_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_search_files(self):
        assert self.file.id is not None, self.file
        url = reverse('podaci_search')
        res = self.client.get(url + '?q=requirements')
        self.assertEqual(res.status_code, 403)

        self.client.force_authenticate(user=self.staff_user)
        res = self.client.get(url + '?q=requirements')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)

        res = self.client.get(url + '?q=banana')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 0)
