from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView

from core.mixins import JSONResponseMixin


class RobotIndex(TemplateView):
    template_name = 'robots/index.jinja'

    def get_context_data(self, **kwargs):
        return {}
