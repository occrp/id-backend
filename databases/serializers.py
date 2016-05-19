from rest_framework import serializers

from .models import ExternalDatabase

class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalDatabase
        fields = ('id', 'agency', 'db_type', 'country', 'paid',
                  'registration_required', 'government_db', 'url',
                  'notes', 'blog_post', 'video_url')
