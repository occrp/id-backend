from podaci import PodaciView
from podaci.filesystem import File, Tag
from django.http import StreamingHttpResponse

class Create(PodaciView):
    template_name = "podaci/tags/create.jinja"

    def get_context_data(self):
        tagname = self.request.POST.get("tag_name", None)
        if not tagname:
            return {"error": "Must supply tag name."}
        tag = Tag(self.fs)
        tag.create(tagname)
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

        tag = Tag(self.fs, id)
        num_displayed = 1000
        tag_cnt, tags = self.fs.list_user_tags(self.request.user, root=tag.id, _size=num_displayed)
        file_cnt, files = self.fs.list_user_files(self.request.user, root=tag.id, _size=num_displayed)
        return {
            "breadcrumbs": self.get_breadcrumbs(),
            "tag": tag,
            "num_files_displayed": min(num_displayed, file_cnt),
            "num_tags": tag_cnt,
            "num_files": file_cnt,
            "result_tags": tags,
            "result_files": files,
        }


class Delete(PodaciView):
    template_name = "podaci/tags/delete.jinja"


class Update(PodaciView):
    template_name = "podaci/tas/update.jinja"


class Zip(PodaciView):
    # FIXME: Move this logic out of the view!
    """
        Return a zip file containing the files belonging to the tag.

        May need to be careful when including huge files. Possibly
        write this as a streamer? (Currently limited to 50MB by Podaci)
    """
    template_name = "NO_TEMPLATE"

    def get(self, request, tid=None, **kwargs):
        from id.apis.podaci import File
        import zipfile
        import StringIO
        archive_name = "id_archive.zip"
        files = request.GET.getlist("files", [])

        if id:
            self.tag = Tag(self.fs, tid)
            archive = self.tag.get_zip()
            archive_name = "%s.zip" % (self.tag.meta["name"])
        elif files:
            # FIXME: This is a duplicate of podaci.Tag.get_zip.
            #        Should be farmed out to somewhere nice.
            #        Probably some kind of ephemeral tag thing.
            _50MB = 50 * 1024 * 1024
            files = [File(self.fs, x) for x in files]
            totalsize = sum([x.meta.get("size", 0) for x in files])
            if totalsize > _50MB:
                return False

            archive = StringIO.StringIO()
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in files:
                    zf.write(f.resident_location(), f.meta["filename"])
            archive.seek(0)
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
            self.tag = Tag(self.fs, id)
            docsetid = o.new_docset_from_tag(self.tag)
        elif files:
            files = [File(self.fs, x) for x in files]
            title = "An unnamed selection of files"
            docsetid = o.new_docset_from_files(title, files)
        else:
            return {"ok": False, "error": "Must supply tag ID or file list."}

        return {"ok": True, "docsetid": docsetid}

