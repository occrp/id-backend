from django.db.models import Q, Func, Value, F
from rest_framework import exceptions, mixins, viewsets

from api_v3.models import Profile
from api_v3.serializers import ProfileSerializer
from .support import JSONApiEndpoint


class ProfilesEndpoint(
        JSONApiEndpoint,
        mixins.UpdateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Profile.objects.filter(Q(is_active=True)).all()

    serializer_class = ProfileSerializer
    filter_fields = ('is_superuser', 'is_staff')

    def perform_update(self, serializer):
        """Allow users to update only own profile.

        Superusers can update the staff flags.
        """
        user = self.request.user

        if user != serializer.instance and not user.is_superuser:
            raise exceptions.NotFound()

        serializer.instance.bio = serializer.validated_data.get('bio')
        serializer.instance.save()

        return serializer

    def get_queryset(self):
        filters = self.extract_filter_params(self.request)

        # If not a super-user, do not allow access
        if self.request.user and not self.request.user.is_superuser:
            return self.queryset.filter(pk=self.request.user.pk)

        if not filters.get('name'):
            return self.queryset
        else:
            return self.queryset.annotate(
                name=Func(
                    Value(' '), F('first_name'), F('last_name'),
                    function='concat_ws'
                )
            ).filter(name__icontains=filters.pop('name'))
