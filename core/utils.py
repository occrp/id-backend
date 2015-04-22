import json
from datetime import datetime
from settings import settings
import tempfile
from oauth2client import tools
from oauth2client import client as oauth2client

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

class Credentials:
    def load_credentials(self):
        try:
            with open(settings.CREDENTIALS_STORE, "r") as fh:
                self.credentials = json_loads(fh.read())
        except IOError:
            print "Credentials file %s does not exist (probably)." % (settings.CREDENTIALS_STORE)
        except ValueError:
            print "Credentials file %s does not contain valid JSON." % (settings.CREDENTIALS_STORE)


    def save_credentials(self):
        with open(settings.CREDENTIALS_STORE, "w+") as fh:
            fh.write(json_dumps(self.credentials))

    def set_credentials(self, site, data):
        self.load_credentials()
        self.credentials[site] = data
        self.save_credentials()

    def get_credentials(self, site):
        self.load_credentials()
        return self.credentials[site]

    def get_oauth2_credentials(self, site, scope):
        # s = self.get_credentials(site)
        # This is stupid
        flow = oauth2client.flow_from_clientsecrets("google_api.cred", scope=scope)
        # credentials = oauth2client.Credentials()
        #if "stored_credentials" in s:
        #    credentials.from_json(s["stored_credentials"])
        # if credentials.invalid:
        credentials = tools.run_flow(flow)
        # s["stored_credentials"] = credentials.to_json()
        # self.set_credentials(site, s)

        return credentials


