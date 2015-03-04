from podaci import PodaciView
from django.http import StreamingHttpResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from copy import copy

class Create(PodaciView):
    template_name = "podaci/files/create.jinja"

    def get_context_data(self):
        res = self.fs.create_file(self.request.FILES["files[]"])

        tag = self.request.POST.get("tag", None)
        if tag:
            res.add_tag(tag)
        return res


class Details(PodaciView):
    template_name = "podaci/files/details.jinja"

    def get_context_data(self, id):
        self.file = self.fs.get_file_by_id(id)
        users = {}
        tags = {}
        notes = []
        for user in self.file.meta["allowed_users"]:
            users[user] = User.objects.get(id=user)
        for tag in self.file.meta["tags"]:
            tags[tag] = self.fs.get_tag(tag)
        notes = copy(self.file.meta["notes"])
        for note in notes:
            u = User.objects.get(id=note["user"])
            note["user_details"] = {
                "username": u.username,
                "email": u.email,
                "first_name": u.profile.first_name,
                "last_name": u.profile.first_name,
            }

        return {
            "file": self.file, 
            "users": users,
            "tags": tags,
            "notes": notes,
        }

class Delete(PodaciView):
    template_name = "podaci/files/create.jinja"


class Download(PodaciView):
    template_name = "NO_TEMPLATE"

    def get(self, request, id, **kwargs):
        self.file = self.fs.get_file_by_id(id)
        response = StreamingHttpResponse(self.file.get(), mimetype=self.file.meta["mimetype"])
        if not bool(request.GET.get("download", True)):
            response['Content-Disposition'] = 'attachment; filename=' + self.file.meta["filename"] 
        return response

class Update(PodaciView):
    template_name = "podaci/files/create.jinja"


class NoteAdd(PodaciView):
    template_name = None

    def get_context_data(self, id):
        self.file = self.fs.get_file_by_id(id)
        print self.request.POST
        text = self.request.POST.get("note_text_markedup", "")
        if not text:
            return {"success": False, "error": "A comment cannot be empty."}

        success = self.file.add_note(text)
        meta = copy(self.file.meta)
        for note in meta["notes"]:
            u = User.objects.get(id=note["user"])
            note["user_details"] = {
                "username": u.username,
                "email": u.email,
                "first_name": u.profile.first_name,
                "last_name": u.profile.first_name,
            }
            note["html"] = render_to_string("podaci/partials/_note.jinja", {"note": note})

        return {
            "success": True,
            "status": success,
            "meta": meta
        }

class NoteUpdate(PodaciView):
    template_name = None

    def get_context_data(self, id):
        pass

class NoteDelete(PodaciView):
    template_name = None

    def get_context_data(self, id):
        pass

class MetaDataAdd(PodaciView):
    template_name = None

