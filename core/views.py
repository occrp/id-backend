from core.models import Notification
from core.serializers import NotificationSerializer

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

class NotificationSeen(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        nid = kwargs.get('pk')
        if nid == "all":
            nots = Notification.objects.filter(user=request.user)
            for n in nots:
                n.seen()
            return JsonResponse({
                "action": "seen",
                "notifications": [n.id for n in nots],
                "unseen_count": Notification.objects.filter(user=request.user, is_seen=False).count()
            })
        else:
            try:
                notification = Notification.objects.get(
                    pk=nid,
                    user=request.user
                )
            except Exception, e:
                return JsonResponse({"error": e})

            notification.seen()
            return JsonResponse({
                "action": "seen",
                "notifications": [notification.id],
                "unseen_count": Notification.objects.filter(user=request.user, is_seen=False).count()
            })


class NotificationStream(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-timestamp")
