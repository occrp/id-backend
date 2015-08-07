from podaci.models import PodaciFile, PodaciTag
from podaci.serializers import FileSerializer, TagSerializer

from rest_framework import mixins
from rest_framework import generics

class Search(generics.ListCreateAPIView):
	pass

class File(generics.ListCreateAPIView):
	pass

class Tag(generics.ListCreateAPIView):
	pass

class Collection(generics.ListCreateAPIView):
	pass

class Note(generics.ListCreateAPIView):
	pass

class MetaData(generics.ListCreateAPIView):
	pass
