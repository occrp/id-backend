from rest_framework_json_api import serializers

from accounts.models import Profile

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'locale'
        )
