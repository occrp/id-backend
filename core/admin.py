from django.contrib import admin
from django.views.generic import TemplateView

from core.models import Notification

class Panel(TemplateView):
    template_name = "admin/panel.jinja"

    def get_context_data(self):
        return {
            "admin_stream": (Notification.objects
                                .order_by("-timestamp"))
        }

