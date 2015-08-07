from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from podaci.serializers import FileSerializer, TagSerializer, CollectionSerializer

from rest_framework import mixins
from rest_framework import generics
from rest_framework import views

class Search(views.APIView):
    pass

class FileList(generics.ListCreateAPIView):
    serializer_class = FileSerializer
    # permission_classes = (IsAuthenticated, CanAlterDeleteProject,)

    def get_queryset(self):
        return PodaciFile.objects.all()

class FileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer

class TagList(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    # permission_classes = (IsAuthenticated, CanAlterDeleteProject,)
    pass

class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TagSerializer

class CollectionList(generics.ListCreateAPIView):
    serializer_class = CollectionSerializer
    # permission_classes = (IsAuthenticated, CanAlterDeleteProject,)

class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CollectionSerializer

class NoteList(generics.ListCreateAPIView):
    pass

class MetaDataList(generics.ListCreateAPIView):
    pass
