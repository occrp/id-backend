from podaci.models import PodaciFile, PodaciTag
from podaci.serializers import FileSerializer, TagSerializer

from rest_framework import mixins
from rest_framework import generics

class File(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = FileSerializer

class Tag(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = TagSerializer
