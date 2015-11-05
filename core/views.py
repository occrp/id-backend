from core.models import Notification, NotificationSubscription
from core.models import channel_components, notification_channel_format
from core.serializers import NotificationSerializer
from core.mixins import NotificationMixin

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

import random

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

class NotificationSubscriptions(APIView):
    # TODO: Needs security
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        print request.auth
        return JsonResponse({
            'notification_subscriptions': [x.channel for x in request.user.notificationsubscription_set.all()]
        })

    def put(self, request, *args, **kwargs):
        channel = request.data.get('channel')
        try:
            request.user.notifications_subscribe(channel)
            return JsonResponse({'result': 'subscribed'})
        except AssertionError, e:
            return JsonResponse({'error': 'invalid channel format'}, status_code=400)
        except TypeError, e:
            return JsonResponse({
                'error': 'you must supply a channel',
                'params': request.data,
            }, status_code=400)

    def delete(self, request, *args, **kwargs):
        channel = request.data.get('channel')
        try:
            cnt = request.user.notifications_unsubscribe(channel)
            if cnt == 0:
                return JsonResponse({'result': 'none', 'found': 0})
            else:
                return JsonResponse({'result': 'unsubscribed', 'found': cnt})
        except AssertionError, e:
            return JsonResponse({'error': 'invalid channel format'}, status_code=400)
        except TypeError, e:
            return JsonResponse({
                'error': 'you must supply a channel',
                'params': request.data,
            }, status_code=418)

class Notify(NotificationMixin, APIView):
    def post(self, request, *args, **kwargs):
        if not request.auth:
            return JsonResponse({"error": "no valid oauth token"}, status_code=403)
        channel = request.data.get('channel')
        if not notification_channel_format.match(channel):
            return JsonResponse({'error': 'invalid channel format'}, status_code=400)

        components = channel_components(channel)
        if components['app'] != request.auth.application.name:
            return JsonResponse({
                'error': 'invalid application name',
                'got': components['app'],
                'expected': request.auth.application.name
            }, status_code=409)

        text = request.data.get('text', None)
        if not text:
            return JsonResponse({'error': 'no text provided'}, status_code=400)
        url = request.data.get('url', None)

        self.notify_channel(channel=channel, text=text, user=request.user, url=url)


class Profile(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        groups = []
        if request.user.is_user: groups.append({'id': 'ticket_requesters', 'name': 'Ticket Requesters'})
        if request.user.is_volunteer: groups.append({'id': 'ticket_requesters', 'name': 'Ticket Volunteers'})
        if request.user.is_staff: groups.append({'id': 'occrp_staff', 'name': 'OCCRP staff'})
        if request.user.network:
            groups.append({'id': 'group:%d' % request.user.network.id, 'name':  request.user.network.long_name})

        return JsonResponse({
            'id': request.user.id,
            'email': request.user.email,
            'display_name': request.user.display_name,
            'is_admin': request.user.is_superuser,
            'is_teapot': random.choice([True, False])
            'groups': groups,
            'locale': request.user.locale,
            'country': request.user.country,
            'notifications_unseen': Notification.objects.filter(user=request.user, is_seen=False).count(),
            'notification_subscriptions': [x.channel for x in request.user.notificationsubscription_set.all()]
        })
