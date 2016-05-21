from django.views.generic import TemplateView
from django.db.models import Sum

from settings import settings

from .models import PodaciTag, PodaciFile, PodaciCollection, HASH_DIRS_DEPTH, HASH_DIRS_LENGTH

class Storage(TemplateView):
    template_name = "admin/storage.jinja"

    def get_context_data(self):
        return {
            "podaci_files": PodaciFile.objects.count(),
            "podaci_tags": PodaciTag.objects.count(),
            "podaci_collections": PodaciCollection.objects.count(),
            "podaci_size": PodaciFile.objects.all().aggregate(Sum('size'))['size__sum'],
            "podaci_data_root": settings.PODACI_FS_ROOT,
            "podaci_data_sharding": "%d deep, %d long" % (HASH_DIRS_DEPTH, HASH_DIRS_LENGTH),
            "podaci_index": "None"
        }


