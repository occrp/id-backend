from datetime import datetime

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.http import JsonResponse

from .models import Notification
from .serializers import NotificationSerializer


def home(request):
    from databases.views import get_databases_index
    return render(request, 'home.jinja', get_databases_index())


def tickets_home(request):
    current_ts = datetime.utcnow().strftime('%s')
    return render(request, 'tickets.jinja', {'current_ts': current_ts})


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
                return JsonResponse({"error": str(e)})

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


class NotificationSubscriptions(APIView):
    # TODO: Needs security
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'notification_subscriptions': [x.channel for x in request.user.notificationsubscription_set.all()]
        })

    def put(self, request, *args, **kwargs):
        channel = request.data.get('channel')
        try:
            request.user.notifications_subscribe(channel)
            return JsonResponse({'result': 'subscribed'})
        except AssertionError, e:
            j = JsonResponse({
                'error': 'invalid channel format.',
                'format_hint': 'app:module:model:instance:action'})
            j.status_code = 400
            return j
        except TypeError, e:
            j = JsonResponse({
                'error': 'you must supply a channel',
                'params': request.data,
            })
            j.status_code = 400
            return j

    def delete(self, request, *args, **kwargs):
        channel = request.data.get('channel')
        try:
            cnt = request.user.notifications_unsubscribe(channel)
            if cnt == 0:
                return JsonResponse({'result': 'none', 'found': 0})
            else:
                return JsonResponse({'result': 'unsubscribed', 'found': cnt})
        except AssertionError as ae:
            j = JsonResponse({'error': 'invalid channel format'})
            j.status_code = 400
            return j
        except TypeError as te:
            j = JsonResponse({
                'error': 'you must supply a channel',
                'params': request.data,
            })
            j.status_code = 418
            return j
