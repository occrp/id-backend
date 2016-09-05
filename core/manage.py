from django.views.generic import TemplateView

from core.models import Notification


class Panel(TemplateView):
    template_name = "manage/panel.jinja"

    def get_context_data(self):
        return {
            "stream": (Notification.objects.order_by("-timestamp")[:50])
        }
