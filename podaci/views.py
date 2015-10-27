import os
import logging
import zipfile
from StringIO import StringIO

from django.db.models import Q
from django.http import FileResponse, HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from ticket.models import Ticket
from podaci.models import PodaciFile, PodaciTag, PodaciCollection
from podaci.serializers import FileSerializer, TagSerializer
from podaci.serializers import CollectionSerializer
from podaci.templatetags import mentions  # noqa

log = logging.getLogger(__name__)


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
        tickets = []
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
                        owner=self.request.user,
                        name=collection.replace("_", " ")))
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
            elif term.startswith("ticket:"):
                tickets.append(term.split("ticket:")[1])
            elif len(term.strip()):
                textterms.append(term)

        text_terms = Q()
        for term in textterms:
            text_terms &= (Q(title__contains=term) |
                           Q(filename__contains=term) |
                           Q(description__contains=term))

        search_terms = base_terms & text_terms & other_terms
        qs = PodaciFile.objects.filter(search_terms)

        for tag in tags:
            qs = qs.filter(tags__name=tag)

        for ticket in tickets:
            qs = qs.filter(tickets__id=ticket)

        for col in collections:
            qs = qs.filter(collections__name=col.name)

        return qs


class FileList(FileQuerySetMixin, generics.ListCreateAPIView):
    serializer_class = FileSerializer
    # we want authenticated users that actually have access to a given file
    permission_classes = (permissions.IsAuthenticated,)


class FileDetail(FileQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated, )


class FileDownload(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, id=None, format=None):
        pfile = get_object_or_404(PodaciFile, pk=id)
        resp = FileResponse(pfile.get_filehandle(request.user))
        resp['Content-Type'] = pfile.mimetype
        resp['Content-Disposition'] = 'filename=' + pfile.filename
        return resp


class ZipDownload(APIView):
    SIZE_LIMIT = 50 * 1024 * 1024

    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, id=None, format=None):
        file_ids = request.GET.getlist('files')
        zstr = StringIO()
        total_size = 0
        with zipfile.ZipFile(zstr, "w", zipfile.ZIP_DEFLATED) as zf:
            # NOTE: this will not detect if files are for missing IDs,
            # ie. if the result set is shorter than the list of file_ids.
            for pfile in PodaciFile.objects.filter(pk__in=file_ids):
                if not os.path.isfile(pfile.local_path):
                    continue
                total_size += pfile.size
                if total_size > self.SIZE_LIMIT:
                    raise HttpResponseBadRequest()
                if not pfile.has_permission(request.user):
                    raise HttpResponseForbidden()
                zf.write(pfile.local_path, pfile.filename)
            zf.close()
        zstr.seek(0)
        resp = FileResponse(zstr)
        resp['Content-Type'] = 'application/zip'
        resp['Content-Disposition'] = 'filename=download.zip'
        return resp


class FileUploadView(generics.CreateAPIView):
    parser_classes = (FileUploadParser,)

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES['files[]']
        ticket = request.POST.get('tickets[]') or None
        if ticket is not None:
            ticket = Ticket.objects.get(pk=ticket)
            if request.user not in ticket.actors():
                raise PermissionDenied()
        pfile = PodaciFile.create_from_filehandle(file_obj, user=request.user,
                                                  ticket=ticket)
        log.debug('File created: %r', pfile)
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
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)


class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CollectionSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return PodaciCollection.objects.filter(owner=self.request.user)

    def patch(self, request, pk, **kwargs):
        collection = PodaciCollection.objects.get(pk=pk,
                                                  owner=self.request.user)

        add_files = request.data.getlist("add_files[]", [])
        remove_files = request.data.getlist("remove_files[]", [])
        for f in add_files:
            try:
                file = PodaciFile.objects.get(id=f)
                if file.has_permission(self.request.user):
                    collection.file_add(file)
            except Exception as e:
                log.exception(e)
                continue

        for f in remove_files:
            try:
                file = PodaciFile.objects.get(id=f)
                if file.has_permission(self.request.user):
                    collection.file_remove(file)
            except Exception as e:
                log.exception(e)
                continue

        return super(CollectionDetail, self).patch(request, pk, **kwargs)
