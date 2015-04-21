import json
from datetime import datetime

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
