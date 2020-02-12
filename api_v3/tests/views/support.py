from django.conf import settings
from django.urls import reverse  # noqa
from django.test import TestCase
from rest_framework.test import APIClient  # noqa
from rest_framework_json_api.utils import (
    get_resource_type_from_serializer, format_field_names)


class ApiTestCase(TestCase):

    JSON_API_CONTENT_TYPE = 'application/vnd.api+json'

    def as_jsonapi_payload(self, serializer_class, obj, update={}):
        data = serializer_class(obj).data
        data.update(update)
        return dict(
            data=dict(
                id=obj.id,
                attributes=format_field_names(
                    data, settings.JSON_API_FORMAT_FIELD_NAMES
                ),
                type=get_resource_type_from_serializer(serializer_class)
            )
        )
