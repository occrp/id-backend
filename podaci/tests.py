from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from id.apis.podaci import *
import os, shutil

class Strawman:
    def __init__(self, username):
        self.id = 1
        self.username = username


class PodaciAPITest(TestCase):
    def setUp(self):
        SERVERS = [{"host": "localhost", "port": 9200}]
        if not os.path.isdir("test_data"):
            os.mkdir("test_data")
        self.fs = FileSystem(SERVERS, "podaci_test", "test_data", user=Strawman("smari"))

    def tearDown(self):
        shutil.rmtree("test_data")

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

