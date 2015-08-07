from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from podaci.serializers import FileSerializer, TagSerializer, CollectionSerializer
from django.db.models import Q

from rest_framework import mixins
from rest_framework import generics
from rest_framework import views

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
    # permission_classes = (IsAuthenticated, CanAlterDeleteProject,)

class FileDetail(FileQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer

class TagList(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    queryset = PodaciTag.objects.all()
    # permission_classes = (IsAuthenticated, CanAlterDeleteProject,)

class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TagSerializer
    queryset = PodaciTag.objects.all()

class CollectionList(generics.ListCreateAPIView):
    serializer_class = CollectionSerializer
    # permission_classes = (IsAuthenticated, CanAlterDeleteProject,)

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)

class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CollectionSerializer

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)


class NoteList(generics.ListCreateAPIView):
    pass

class MetaDataList(generics.ListCreateAPIView):
    pass
