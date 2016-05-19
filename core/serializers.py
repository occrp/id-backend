from rest_framework import serializers

from .models import Notification, AuditLog


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'timestamp', 'is_seen', 'text', 'url', 'channel')

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ('id', "user", "level", "module", "filename", "lineno",
                "funcname", "message", "process", "thread", "ip", "timestamp")
