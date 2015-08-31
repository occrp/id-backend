from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from podaci.serializers import FileSerializer, TagSerializer, CollectionSerializer
from django.db.models import Q

from rest_framework import mixins
from rest_framework import generics
from rest_framework import views
from rest_framework import permissions
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

class HasPodaciFileAccess(permissions.BasePermission):

    def has_permission(self, request, view):
        # a read-only method?
        if request.method in permissions.SAFE_METHODS:
            return PodaciFile.objects.get(id=request.kwargs.get('pk', None)).has_permission(request.user)

        # otherwise...
        return PodaciFile.objects.get(id=request.kwargs.get('pk', None)).has_write_permission(request.user)


class HasPodaciCollectionAccess(permissions.BasePermission):

    def has_permission(self, request, view):
        # simple enough
        # only the owner has access to a collection
        return ( PodaciCollection.objects.get(id=request.kwargs.get('pk', None)).owner == request.user )

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
        collections = []

        for term in terms:
            if term.startswith("#"):
                tag = term.split("#")[1]
                tags.append(tag)
            elif term.startswith("in:"):
                collection = term.split("in:")[1]
                if collection == "all":
                    collections = []
                elif collection == "mine":
                    collections.extend(PodaciCollection.objects.filter(
                        owner=self.request.user))
                elif collection == "shared":
                    collections.extend(PodaciCollection.objects.filter(
                        owner=self.request.user, shared=True))
                else:
                    collections.extend(PodaciCollection.objects.filter(
                        owner=self.request.user, name=collection.replace("_", " ")))
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

        for col in collections:
            search_terms &= Q(collections__in=[col])

        print search_terms
        return PodaciFile.objects.filter(search_terms)


class FileList(FileQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = FileSerializer
    # we want authenticated users that actually have access to a given file
    permission_classes = (permissions.IsAuthenticated, HasPodaciFileAccess,)


class FileDetail(FileQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated, HasPodaciFileAccess,)


class FileUploadView(generics.CreateAPIView):
    parser_classes = (FileUploadParser,)

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES['files[]']
        pfile = PodaciFile()
        pfile.create_from_filehandle(file_obj)
        print "Created: ", pfile
        serializer = FileSerializer(pfile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TagList(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    queryset = PodaciTag.objects.all()


class TagDetail(generics.RetrieveAPIView):
    serializer_class = TagSerializer
    queryset = PodaciTag.objects.all()


class CollectionList(generics.ListCreateAPIView):
    serializer_class = CollectionSerializer
    permission_classes = (permissions.IsAuthenticated, HasPodaciCollectionAccess,)

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)


class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CollectionSerializer
    permission_classes = (permissions.IsAuthenticated, HasPodaciCollectionAccess,)

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)

    def patch(self, request, pk, **kwargs):
        try:
            collection = PodaciCollection.objects.get(pk=pk,
                            owner=self.request.user)
        except:
            print "ERRORRRRRR"

        add_files = request.data.getlist("add_files[]", [])
        remove_files = request.data.getlist("remove_files[]", [])
        for f in add_files:
            try:
                file = PodaciFile.objects.get(id=f)
                if file.has_permission(self.request.user):
                    collection.file_add(file)
            except Exception, e:
                print "Error:", e
                continue

        for f in remove_files:
            try:
                file = PodaciFile.objects.get(id=f)
                if file.has_permission(self.request.user):
                    collection.file_remove(file)
            except Exception, e:
                print "Error:", e
                continue

        return super(CollectionDetail, self).patch(request, pk, **kwargs)


class NoteList(generics.ListCreateAPIView):
    pass

class MetaDataList(generics.ListCreateAPIView):
    pass
