from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.settings import api_settings
from rest_framework_json_api import serializers

from api_v3.models import Responder, Subscriber


class ResponderSubscriberSerializer(serializers.ModelSerializer):

    UNIQUENESS_VALIDATORS = [
        UniqueTogetherValidator(
            queryset=Subscriber.objects.all(),
            fields=('user', 'ticket'),
            message='Subscriber already exists.'
        ),
        UniqueTogetherValidator(
            queryset=Responder.objects.all(),
            fields=('user', 'ticket'),
            message='User is a responder.'
        )
    ]

    def run_validation(self, data=empty):
        """Remap non field error key to the user key to keep consistency."""
        try:
            return super(
                ResponderSubscriberSerializer, self
            ).run_validation(data)
        except ValidationError as error:
            error.detail['user'] = error.detail.pop(
                api_settings.NON_FIELD_ERRORS_KEY, None
            )
            raise error
