from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.settings import api_settings
from rest_framework_json_api import serializers

from api_v3.models import Responder, Subscriber


class ResponderSubscriberSerializer(serializers.ModelSerializer):

    EMAIL_SUBSCRIBER_ERROR_MESSAGE = 'Email already subscribed.'
    SUBSCRIBER_ERROR_MESSAGE = 'Subscriber already exists.'
    RESPONDER_ERROR_MESSAGE = 'User is a responder.'

    UNIQUENESS_VALIDATORS = [
        UniqueTogetherValidator(
            queryset=Subscriber.objects.all(),
            fields=('user', 'ticket'),
            message=SUBSCRIBER_ERROR_MESSAGE
        ),
        UniqueTogetherValidator(
            queryset=Responder.objects.all(),
            fields=('user', 'ticket'),
            message=RESPONDER_ERROR_MESSAGE
        )
    ]
    EMAIL_UNIQUENESS_VALIDATORS = [
        UniqueTogetherValidator(
            queryset=Subscriber.objects.all(),
            fields=('ticket', 'email'),
            message=EMAIL_SUBSCRIBER_ERROR_MESSAGE
        ),
    ]

    def run_validation(self, data=empty):
        """Remap non field error key to the user key to keep consistency."""
        try:
            return super(
                ResponderSubscriberSerializer, self
            ).run_validation(data)
        except ValidationError as error:
            messages = error.detail.pop(api_settings.NON_FIELD_ERRORS_KEY, None)

            if messages and self.EMAIL_SUBSCRIBER_ERROR_MESSAGE in messages:
                error.detail['email'] = messages
            else:
                error.detail['user'] = messages

            raise error
