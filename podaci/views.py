from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from podaci.serializers import FileSerializer, TagSerializer, CollectionSerializer
from django.db.models import Q

from rest_framework import mixins
from rest_framework import generics
from rest_framework import views
from rest_framework import permissions


class HasPodaciFileAccess(permissions.BasePermission):
    
    has_permission(self, request, view):
        # a read-only method?
        if request.method in permissions.SAFE_METHODS:
            return PodaciFile.objects.get(id=request.kwargs.get('pk', None)).has_permission(request.user)
        
        # otherwise...
        return PodaciFile.objects.get(id=request.kwargs.get('pk', None)).has_write_permission(request.user)


class HasPodaciCollectionAccess(permissions.BasePermission):
    
    has_permission(self, request, view):
        # simple enough
        # only the owner has access to a collection
        return ( PodaciCollection.objects.get(id=request.kwargs.get('pk', None)).owner == request.user )


class Search(views.APIView):
    pass


class FileQuerySetMixin(object):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return PodaciFile.objects.all()
        terms = (Q(public_read=True) |
                Q(allowed_users_read__in=self.request.user))

        if self.request.user.is_staff:
            terms |= Q(staff_read=True)

        return PodaciFile.objects.filter(terms)


class FileList(FileQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = FileSerializer
    # we want authenticated users that actually have access to a given file
    permission_classes = (permissions.IsAuthenticated, HasPodaciFileAccess,)


class FileDetail(FileQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated, HasPodaciFileAccess,)


class TagList(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    queryset = PodaciTag.objects.all()


class TagDetail(generics.RetrieveAPIView):
    serializer_class = TagSerializer
    queryset = PodaciTag.objects.all()


class CollectionList(generics.ListCreateAPIView):
    serializer_class = CollectionSerializer
    permission_classes = (IsAutenticated, HasPodaciCollectionAccess,)

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)


class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CollectionSerializer
    permission_classes = (IsAutenticated, HasPodaciCollectionAccess,)

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)


class NoteList(generics.ListCreateAPIView):
    pass

class MetaDataList(generics.ListCreateAPIView):
    pass
