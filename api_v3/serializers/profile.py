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
        view = self.context.get('view') if self.context else None

        if not view:
            return 0
        else:
            return view.filter_queryset(view.get_queryset()).count()

    def to_representation(self, obj):
        request = self.context.get('request', None)

        data = super(ProfileSerializer, self).to_representation(obj)

        if request and request.user and request.user.is_superuser:
            return data

        # For regular users, make sure others email is not displayed
        if request and request.user != obj:
            data.pop('email')

        return data
