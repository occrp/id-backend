from django.contrib import admin
from .models import ExternalDatabase
from .forms import ExternalDatabaseForm
from django.views.generic import CreateView, UpdateView, DeleteView



class ExternalDatabaseCreate(CreateView):
    form_class = ExternalDatabaseForm
    template_name = "admin/external_database.jinja"
    success_url = '/admin/external_database'

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = ExternalDatabase.objects.all()
        kwargs['action'] = 'create'
        return super(CreateView, self).get_context_data(**kwargs)

class ExternalDatabaseUpdate(UpdateView):
    form_class = ExternalDatabaseForm
    template_name = "admin/external_database.jinja"
    success_url = '/admin/external_database/' 

    def get_object(self, queryset=None):
        return ExternalDatabase.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['pk'] = self.kwargs['pk']
        kwargs['action'] = 'update'
        kwargs['object_list'] = ExternalDatabase.objects.all()

        return super(UpdateView, self).get_context_data(**kwargs)

class ExternalDatabaseDelete(DeleteView):
    form_class = ExternalDatabaseForm
    template_name = "admin/external_database.jinja"
    success_url = '/admin/external_database'

    def get_object(self, queryset=None):
        return ExternalDatabase.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['pk'] = self.kwargs['pk']
        kwargs['action'] = 'delete'
        kwargs['obj_info'] = self.get_object()
        kwargs['object_list'] = ExternalDatabase.objects.all()

        return super(DeleteView, self).get_context_data(**kwargs)

