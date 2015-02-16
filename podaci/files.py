from podaci import PodaciView
from django.http import StreamingHttpResponse
from django.contrib.auth.models import User

class Create(PodaciView):
    template_name = "podaci/files/create.html"

    def get_context_data(self):
        res = self.fs.create_file(self.request.FILES["files[]"])

        tag = self.request.POST.get("tag", None)
        if tag:
            res.add_tag(tag)
        return res


class Details(PodaciView):
    template_name = "podaci/files/details.html"

    def get_context_data(self, id):
        self.file = self.fs.get_file_by_id(id)
        users = {}
        tags = {}
        for user in self.file.meta["allowed_users"]:
            users[user] = User.objects.get(id=user)
        for tag in self.file.meta["tags"]:
            tags[tag] = self.fs.get_tag(tag)
        return {
            "file": self.file, 
            "users": users,
            "tags": tags
        }

class Delete(PodaciView):
    template_name = "podaci/files/create.html"


class Download(PodaciView):
    template_name = "NO_TEMPLATE"

    def get(self, request, id, **kwargs):
        self.file = self.fs.get_file_by_id(id)
        response = StreamingHttpResponse(self.file.get(), mimetype=self.file.meta["mimetype"])
        if not bool(request.GET.get("download", True)):
            response['Content-Disposition'] = 'attachment; filename=' + self.file.meta["filename"] 
        return response

class Update(PodaciView):
    template_name = "podaci/files/create.html"
