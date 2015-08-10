from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from podaci.serializers import FileSerializer, TagSerializer, CollectionSerializer
from django.db.models import Q

from rest_framework import mixins
from rest_framework import generics
from rest_framework import views

class FileQuerySetMixin(object):
    def get_base_terms(self):
        if self.request.user.is_superuser:
            return Q()

        terms = (Q(public_read=True) |
                 Q(allowed_users_read__in=[self.request.user]))

        if self.request.user.is_staff:
            terms |= Q(staff_read=True)

        return terms

    def get_queryset(self):
        terms = self.get_base_terms()
        return PodaciFile.objects.filter(terms)

class Search(FileQuerySetMixin, generics.ListAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        q = self.request.GET.get("q", None)
        if not q:
            return super(Search, self).get_queryset()

        base_terms = self.get_base_terms()

        terms = q.split(" ")
        textterms = []
        tags = []
        other_terms = Q()
        collections = None

        for term in terms:
            if term.startswith("#"):
                tag = term.split("#")[1]
                tags.append(tag)
            elif term.startswith("in:"):
                collection = term.split("in:")[1]
                if collection == "all":
                    collections = None
                elif collection == "mine":
                    collections = PodaciCollection.objects.filter(
                        owner=request.user)
                elif collection == "shared":
                    collections = PodaciCollection.objects.filter(
                        owner=request.user, shared=True)
                else:
                    collections = PodaciCollection.objects.filter(
                        owner=request.user, name=collection)
            elif term.startswith("mime:"):
                mime = term.split("mime:")[1]
                other_terms |= Q(mimetype=mime)
            elif term.startswith("size:"):
                size = term.split("size:")[1]
                if size[0] == ">":
                    other_terms |= Q(size__gt=size[1:])
                elif size[0] == "<":
                    other_terms |= Q(size__lt=size[1:])
                else:
                    other_terms |= Q(size=size)
            else:
                textterms.append(term)

        tag_terms = Q()
        for tag in tags:
            tag_terms &= Q(tags__name=tag)

        text_terms = Q()
        for term in textterms:
            text_terms &= (Q(name__contains=term) |
                            Q(filename__contains=term) |
                            Q(description__contains=term))

        search_terms = base_terms & text_terms & tag_terms & other_terms

        if collections:
            search_terms &= Q(collections__in=collections)

        print search_terms
        return PodaciFile.objects.filter(search_terms)


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
