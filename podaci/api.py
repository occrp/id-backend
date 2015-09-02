import requests
from requests.auth import HTTPBasicAuth
from core.utils import Credentials, sha256_to_uuid, json_dumps, json_loads
from uuid import uuid4
import rfc6266

class OverviewAPI:
    ENDPOINTS = {
        "upload":           "https://%(server)s/api/v1/files/%(guid)s",
        "finish_docset":    "https://%(server)s/api/v1/files/finish",
        "create_docset":    "https://%(server)s/api/v1/document-sets"
    }

    def __init__(self, server, apitoken):
        self.server = server
        self.apitoken = apitoken

    def _auth(self, apitoken=None):
        if not apitoken:
            apitoken = self.apitoken
        return HTTPBasicAuth(apitoken, "x-auth-token")

    def _endpoint(self, name):
        return self.ENDPOINTS[name]

    def new_docset_from_tag(self, tag):
        count, files = tag.list_files()
        docset = self.new_docset_from_files(tag["name"], files)
        return docset

    def new_docset_from_files(self, title, files=[]):
        docsetid, token = self.create_docset(title)
        self.mass_upload(files, token=token)
        self.finish_docset(token=token)
        return docsetid

    def mass_upload(self, files=[], token=None):
        for f in files:
            self.upload_file(f, token)

    def create_docset(self, title):
        url = self._endpoint("create_docset") % {"server": self.server}
        json = {
            "title": title
        }
        headers = {
            "Content-Type": "application/json"
        }
        par = {}

        res = requests.post(url, auth=self._auth(), data=json_dumps(json),
                            params=par, headers=headers)
        result = json_loads(res.content)
        return result["documentSet"]["id"], result["apiToken"]["token"]

    def finish_docset(self, docsetid=None, token=None):
        #if not docsetid:
        #    docsetid = str(uuid4())

        url = self._endpoint("finish_docset") % {"server": self.server}
        json = {
            "lang": "en",
            "split_documents": False,
            "supplied_stop_words": "",
            "important_words": ""
        }
        par = {}
        headers = {
            "Content-Type": "application/json"
        }
        if docsetid:
            par["documentSetId"] = docsetid

        res = requests.post(url, auth=self._auth(token), data=json_dumps(json),
                            params=par, headers=headers)
        return res.status_code

    def upload_file(self, f, token=None):
        done = False
        f["extra"]["overview_guid"] = str(sha256_to_uuid(f["hash"]))
        f._sync()
        url = self._endpoint("upload") % {"guid": f["extra"]["overview_guid"], "server": self.server}
        par = {}
        headers = {
            "Content-Disposition": "%s" % rfc6266.build_header(f["filename"]),
            "Content-Length": f["size"]
        }
        while not done:
            res = requests.post(url,
                auth=self._auth(token),
                params=par,
                headers=headers,
                data=f.get_filehandle())
            if res.status_code == requests.codes.created:
                done = True
