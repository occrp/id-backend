from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from settings.settings import *
from podaci.filesystem import *
import os, shutil

class Strawman:
    def __init__(self, username):
        self.id = 1
        self.username = username


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

