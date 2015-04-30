import json
import httplib2
import argparse
import os.path
from datetime import datetime
from settings import settings
import tempfile
from oauth2client import tools as oauth2tools
from oauth2client import client as oauth2client
from oauth2client import file as oauth2file
from uuid import UUID

def convert_group_to_select2field_choices(group):
    result = []

    for i in group:
        result.append((i.id, i.display_name))

    return result

def json_dumps(data):
    # Note: This is *EXTREMELY* naive; in reality, you'll need
    # to do much more complex handling to ensure that arbitrary
    # objects -- such as Django model instances or querysets
    # -- can be serialized as JSON.
    def handledefault(o):
        if isinstance(o, datetime):
            return o.strftime("%s")
        if hasattr(o, "to_json"):
            return o.to_json()
        elif hasattr(o, "__dict__"):
            return o.__dict__
        else:
            raise ValueError("Type %s is not JSON serializable. Add to_json() or __dict__", type(o))
    return json.dumps(data, default=handledefault)

def json_loads(s):
    return json.loads(s)

def file_to_str(filename):
    with open(filename, 'r') as f:
        return f.read()

def version():
    return settings.ID_VERSION

def sha256_to_uuid(sha):
    return UUID(bytes=sha[:16], version=5)

class Credentials:
    def __init__(self):
        self.credentials = {}

    def load_credentials(self):
        credpath = os.path.join(settings.CREDENTIALS_DIR, "db.json")
        try:
            with open(credpath, "r") as fh:
                self.credentials = json_loads(fh.read())
        except IOError:
            print "Credentials file %s does not exist (probably)." % (settings.CREDENTIALS_STORE)
        except ValueError:
            print "Credentials file %s does not contain valid JSON." % (settings.CREDENTIALS_STORE)

    def save_credentials(self):
        with open(settings.CREDENTIALS_STORE, "w+") as fh:
            fh.write(json_dumps(self.credentials))

    def set(self, site, data):
        return self.set_credentials(site, data)

    def get(self, site, var=None):
        return self.get_credentials(site, var)

    def set_credentials(self, site, data):
        self.load_credentials()
        self.credentials[site] = data
        self.save_credentials()

    def get_credentials(self, site, var=None):
        self.load_credentials()
        site = self.credentials.get(site, {})
        if not var: return site
        var = site.get(var, {})
        return var

    def get_oauth2_http(self, site, scope):
        creds = self.get_oauth2_credentials(site, scope)
        http = httplib2.Http()
        http = creds.authorize(http)
        return http

    def get_oauth2_credentials(self, site, scope):
        # TODO: This will probably fail if we fetch two tokens with different
        #       scopes.
        credpath = os.path.join(settings.CREDENTIALS_DIR, "%s.cred" % site)
        tokenpath = os.path.join(settings.CREDENTIALS_DIR, "%s.dat" % site)
        flow = oauth2client.flow_from_clientsecrets(credpath, scope=scope)

        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[oauth2tools.argparser])
        args = parser.parse_args([])
        storage = oauth2file.Storage(tokenpath)
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = oauth2tools.run_flow(flow, storage, args)

        return credentials

