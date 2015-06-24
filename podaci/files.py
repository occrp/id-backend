from podaci import PodaciView
from django.http import StreamingHttpResponse
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.template.loader import render_to_string
from podaci.models import PodaciFile, PodaciTag

class Create(PodaciView):
    template_name = "podaci/files/create.jinja"

    def get_context_data(self):
        f = PodaciFile()
        uploadedfile = self.request.FILES.get("files[]", "")
        if uploadedfile == "":
            return None
        f.create_from_filehandle(uploadedfile, user=self.request.user)
        tag = self.request.POST.get("tag", None)
        try:
            tag = PodaciTag.objects.get(id=tag)
            f.add_tag(tag)
        except:
            pass
        return f


class Details(PodaciView):
    template_name = "podaci/files/details.jinja"

    def get_context_data(self, id):
        self.file = PodaciFile.objects.get(id=id)
        return {
            "file": self.file, 
            "users": self.file.allowed_users_read.all(),
            "tags": self.file.tags.all(),
            "notes": self.file.notes.all(),
        }

class Delete(PodaciView):
    template_name = "podaci/files/create.jinja"

    def get_context_data(self, id):
        try:
            f = PodaciFile.objects.get(id=id)
        except Exception, e:
            return {"id": id, "deleted": False, "error": e}
        status = f.delete()
        return {"id": id, "deleted": status}

class Download(PodaciView):
    template_name = "NO_TEMPLATE"

    def get(self, request, id, **kwargs):
        f = PodaciFile.objects.get(id=id)
        response = StreamingHttpResponse(f.get(), content_type=f.meta["mimetype"])
        if not bool(request.GET.get("download", True)):
            response['Content-Disposition'] = 'attachment; filename=' + f.meta["filename"] 
        return response

class Update(PodaciView):
    template_name = "podaci/files/create.jinja"


class NoteAdd(PodaciView):
    template_name = None

    def get_context_data(self, id):
        self.file = File.objects.get(id=id)

        text = self.request.POST.get("note_text_markedup", "")
        if not text:
            return {"success": False, "error": "A comment cannot be empty."}

        success = self.file.add_note(text)
        html = []
        for note in self.file.notes.all():
            html.append(render_to_string("podaci/partials/_note.jinja", {"note": note}))

        return {
            "success": True,
            "status": success,
            "html": html
        }

class NoteUpdate(PodaciView):
    template_name = None

    def get_context_data(self, fid, nid, text):
        self.file = File.objects.get(id=fid)
        return {'status': self.file.note_update(nid, text)}

class NoteDelete(PodaciView):
    template_name = None

    def get_context_data(self, fid, nid):
        self.file = File.objects.get(id=fid)
        return {'status': self.file.note_delete(nid)}

class MetaDataAdd(PodaciView):
    template_name = None
