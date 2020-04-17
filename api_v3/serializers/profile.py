from django.conf import settings
from rest_framework import fields
from rest_framework_json_api import serializers

from api_v3.models import Profile, Ticket


class ProfileSerializer(serializers.ModelSerializer):

    tickets_count = fields.SerializerMethodField()

    class Meta:
        model = Profile
        read_only_fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'locale'
        )
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'bio',
            'locale',
            'tickets_count'
        )

    def get_tickets_count(self, obj):
        if obj.is_superuser:
            return Ticket.objects.count()
        else:
            return Ticket.filter_by_user(obj).count()

    def to_representation(self, obj):
        request = self.context.get('request', None)

        data = super(ProfileSerializer, self).to_representation(obj)

        if request and request.user and request.user.is_superuser:
            return data

        # For regular users, make sure others email is not displayed
        if request and request.user != obj:
            data.pop('email')

        return data

    # Adds extra application related metas.
    def get_root_meta(self, resource, many):
        if not self.context.get('add_misc', None):
            return {}

        return {
            'member_centers': sorted(settings.MEMBER_CENTERS),
            'expense_scopes': sorted(settings.EXPENSE_SCOPES)
        }
