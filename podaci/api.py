import requests
from requests.auth import HTTPBasicAuth
from core.utils import Credentials, sha256_to_uuid, json_dumps
from uuid import uuid4

class OverviewAPI:
    ENDPOINTS = {
        "upload":           "https://%(server)s/api/v1/files/%(guid)s",
        "create_docset":    "https://%(server)s/api/v1/files/finish"
    }

    def __init__(self, server, apitoken):
        self.server = server
        self.apitoken = apitoken

    def _auth(self, apitoken=None):
        if not apitoken:
            apitoken = self.apitoken
        return HTTPBasicAuth(apitoken, "x-auth-token")

    def _endpoint(self, name):
        return self.ENDPOINTS % {"server": self.server}

    def new_docset_from_tag(self, tag):
        count, files = tag.list_files()
        docset = self.new_docset(files)
        return docset

    def new_docset_from_files(self, files=[]):
        self.mass_upload(files)
        docset = self.create_docset()
        return docset

    def mass_upload(self, files=[]):
        for f in files:
            self.upload_file(f)

    def create_docset(self, docsetid=None):
        if not docsetid:
            docsetid = str(uuid4())

        url = self._endpoint("create_docset")
        json = {
            "lang": "en",
            "split_documents": False,
            "supplied_stop_words": "",
            "important_words": ""
        }
        par = {
            "documentSetId": docsetid
        }
        res = requests.post(url, auth=self._auth(), data=json_dumps(json), params=par)

    def upload_file(self, f):
        done = False
        f["extra"]["overview_guid"] = str(sha256_to_uuid(f["hash"]))
        f._sync()
        url = self._endpoint("upload") % {"guid": f["extra"]["overview_guid"]}
        par = {}
        while not done:
            res = requests.post(url, 
                auth=self._auth(),
                params=par,
                files={f["filename"]: f.get_filehandle()})
            if res.status_code == requests.codes.ok:
                done = True

