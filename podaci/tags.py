from podaci import PodaciView
from django.http import StreamingHttpResponse

class Create(PodaciView):
    template_name = "podaci/tags/create.jinja"

    def get_context_data(self):
        tagname = self.request.POST.get("tag_name", None)
        if not tagname:
            return {"error": "Must supply tag name."}
        tag = PodaciTag()
        tag.name = tagname
        tag.save()
        parent = self.request.POST.get("tag_parents", None)
        if parent:
            tag.parent_add(parent)

        return {
            "tag": tag
        }


class List(PodaciView):
    template_name = None

    def get_context_data(self):
        # FIXME: What happens if a user has >1000 tags?
        num_displayed = 1000
        tag_cnt, tags = self.fs.list_user_tags(self.request.user, root=None, _size=num_displayed)
        if self.request.GET.get("structure", "") == "select2":
            return {"pagination": {"more": False}, "results": [{"id": x.id, "text": x["name"]} for x in tags]}
        else:
            return {
                "num_tags": tag_cnt,
                "result_tags": tags,
            }


class Details(PodaciView):
    template_name = "podaci/tags/details.jinja"

    def get_context_data(self, id):
        while self.breadcrumb_exists(id):
            self.breadcrumb_pop()
        self.breadcrumb_push(id)

        tag = PodaciTag(self.fs, id)
        tags = PodaciTag.objects.filter(allowed_users_read__contains=self.request.user, parents__contains=tag)
        files = PodaciFile.objects.filter(allowed_users_read__contains=self.request.user, tags__contains=tag)
        return {
            "breadcrumbs": self.get_breadcrumbs(),
            "tag": tag,
            "num_tags": tags.count(),
            "num_files": files.count(),
            "result_tags": tags,
            "result_files": files,
        }


class Delete(PodaciView):
    template_name = "podaci/tags/delete.jinja"


class Update(PodaciView):
    template_name = "podaci/tas/update.jinja"


class Zip(PodaciView):
    # FIXME: Move this logic out of the view!
    # FIXME: May need to be careful when including huge files. Possibly
    #          write this as a streamer? (Currently limited to 50MB)
    """
        Return a zip file containing the files belonging to the tag.
    """
    template_name = "NO_TEMPLATE"

    def get(self, request, tid=None, **kwargs):
        import zipfile
        import StringIO
        archive_name = "id_archive.zip"
        files = request.GET.getlist("files", [])

        if id:
            tag = PodaciTag.objects.get(tid)
            archive_name = "%s.zip" % (tag.name)
            archive = tag.get_zip()
        elif files:
            tag = PodaciTag()
            tag.name = "Temporary"
            tag.save()
            files = PodaciFile.objects.filter(id__in=files)
            for f in files:
                files.tags.add(tag)
            archive = tag.get_zip()
            tag.delete()
        else:
            raise ValueError("Must supply tag ID or file list.")

        response = StreamingHttpResponse(archive, content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename=' + archive_name
        return response


class Overview(PodaciView):
    # FIXME: Move this logic out of the view!
    """
        ...
    """
    template_name = "NO_TEMPLATE"

    def get_context_data(self, id=None, **kwargs):
        from podaci.api import OverviewAPI
        files = self.request.GET.getlist("files", [])

        o = OverviewAPI("www.overviewproject.org", "ekykvx3qj0jr5fbrzdqtpcrp0")

        if id:
            tag = PodaciTag.objects.get(id)
            docsetid = o.new_docset_from_tag(tag)
        elif files:
            files = PodaciFile.objects.filter(id__in=files)
            title = "An unnamed selection of files"
            docsetid = o.new_docset_from_files(title, files)
        else:
            return {"ok": False, "error": "Must supply tag ID or file list."}

        return {"ok": True, "docsetid": docsetid}

