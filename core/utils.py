from datetime import datetime, date
import json

from django.db.models.query import QuerySet
from django.db.models.sql.query import Query

from settings import settings


def convert_group_to_select2field_choices(group):
    result = []

    for i in group:
        result.append((i.id, "%s [%s%s]" % (i.display_name, ["", "S"][i.is_staff])))

    return result


def json_default(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    elif isinstance(o, Query):
        raise ValueError("Cannot JSON serialize a Query for security reasons.")
    elif isinstance(o, QuerySet):
        # This might not be sufficient
        return [x.id for x in o]
    elif hasattr(o, "to_json"):
        return o.to_json()
    elif hasattr(o, "__dict__"):
        return o.__dict__
    else:
        raise ValueError("Type %s is not JSON serializable. Add to_json() or __dict__", type(o))


def json_dumps(data):
    # Note: This is *EXTREMELY* naive; in reality, you'll need
    # to do much more complex handling to ensure that arbitrary
    # objects -- such as Django model instances or querysets
    # -- can be serialized as JSON.
    return json.dumps(data, default=json_default)


def json_loads(s):
    return json.loads(s)


def version():
    return settings.ID_VERSION
