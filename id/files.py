from django.http import HttpResponseRedirect
from django.views.generic import View, TemplateView
from id.mixins import JSONResponseMixin, MessageMixin
from django.core.urlresolvers import reverse



class ListFilesHandler(View, JSONResponseMixin):

    # FIXME: Auth
    # @role_in('user', 'volunteer', 'staff', 'admin')
    #def get(self, folder_id):
        #files = Drive.system_instance().list_files(folder_id)
        # self.render_json_response(files)
    def get(self, request, folder_id):
        return super(ListFilesHandler, self).get(request)

    def get_context_data(self):
        return {}


class RemoveFileHandler(TemplateView):
    # FIXME: Auth
    # @role_in('user', 'volunteer', 'staff', 'admin')
    def post(self):
        file_id = self.request.POST['file_id']
        folder_id = self.request.POST['folder_id']
        # Drive.system_instance().remove_from_folder([file_id], folder_id)
        pass


class UploadFileHandler(TemplateView, MessageMixin):

    # FIXME: Auth
    #@drive_decorator.oauth_required
    #@role_in('user', 'volunteer', 'staff', 'admin')
    def post(self):
        file_ids = json.loads(self.request.POST['file_ids'])
        #obj = ndb.Key(urlsafe=self.request.POST['key']).get()
        #if self.request.POST['first_file']:
        #    self.add_message(_('File(s) successfully attached.'), 'success')
        #d = Drive(http=drive_decorator.http())
        #d.upload(file_ids, obj)

        # join the user into a ticket if they're not already attached to it.
        #if (isinstance(obj, models.Ticket) and
        #        self.profile.key not in obj.actors()):
        #    obj.join_user(self.profile)


class DirectUploadFileHandler(TemplateView, MessageMixin):
    # FIXME: Auth
    # @role_in('admin')
    def get(self):
        #NB this one is just for testing
        # FIXME: This is stupid.
        self.response.write('''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
        <input type="text" name="key" value="ahtkZXZ-aW52ZXN0aWdhdGl2ZS1kYXNoYm9hcmRyEwsSBlRpY2tldBiAgICAgMCvCgw"/>
      <p><input type=file name=file1>
        <input type=file name=file2>
         <input type=submit value=Upload>
    </form>
    ''')

    #@drive_decorator.oauth_required # XXX is this needed?
    # FIXME: Auth
    # @role_in('user', 'volunteer', 'staff', 'admin')
    def post(self):
        '''
        accept files directly for upload to GAE
        required values are:
          0+ files
          key for the object
        '''
        # d = Drive()
        # obj = ndb.Key(urlsafe=self.request.POST['key']).get()
        # if not self.profile.can_write_to(obj):
        #     return self.abort(401)

        # if (isinstance(obj, models.Ticket) and
        #         self.profile.key not in obj.actors()):
        #     obj.join_user(self.profile)

        # filenum = 1
        # while True:
        #     field = self.request.POST.get('file%s' % filenum, None)
        #     print(self.request.POST.keys())
        #     if field in (None, ''): # will be None if there is no field, u'' if field is empty. Annoyingly, FieldStorage is not True
        #         break
        #     obj._add_file(fh = field.file, title = field.filename)
        #     self.add_message(_('Successfully attached %s' % field.filename), 'success')
        #     filenum += 1
        return HttpResponseRedirect(reverse('ticket_list'))

class UploadCheck(TemplateView, JSONResponseMixin):

    # @drive_decorator.oauth_aware
    # @role_in('user', 'volunteer', 'staff', 'admin')
    # FIXME: Auth
    def get(self):
        pass
        # if drive_decorator.has_credentials():
        #     try:
        #         Drive(http=drive_decorator.http()).about()
        #         self.render_json_response({
        #             'status': 'success',
        #             'email_address': self.profile.email
        #         })
        #     except AccessTokenRefreshError:
        #         self.render_json_response({'status': 'authorize'})
        #     except DriveError:
        #         self.render_json_response({'status': 'error'})
        # else:
        #     self.render_json_response({'status': 'authorize'})
