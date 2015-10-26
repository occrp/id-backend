from django.db import models

######## External databases ############
class ExternalDatabase(models.Model, DisplayMixin):
    agency = models.CharField(max_length=500, blank=False, verbose_name=_('Agency / Name'))
    # agency_lower = models.ComputedProperty(lambda self: self.agency.lower())
    db_type = models.CharField(max_length=20, choices=DATABASE_TYPES,
                               verbose_name=_('Type of Database'))
    country = models.CharField(max_length=20, choices=DATABASE_COUNTRIES,
                               verbose_name=_('Country'))
    paid = models.BooleanField(default=False, verbose_name=_('Paid Database'))
    registration_required = models.BooleanField(default=False, verbose_name=_('Registration Required'))
    government_db = models.BooleanField(default=False, verbose_name=_('Government Database'))
    url = models.URLField(max_length=2000   , blank=False, verbose_name=_('URL'))
    notes = models.TextField(verbose_name=_('Notes'))
    blog_post = models.URLField(verbose_name=_('Blog Post'))
    video_url = models.URLField(verbose_name=_('YouTube Video Url'))

    def continent(self):
        return self._find_in_grouping(CONTINENTS)

    def region(self):
        return self._find_in_grouping(REGIONS)

    def _find_in_grouping(self, grouping):
        matches = [(k,v) for (k,v) in grouping.items() if self.country in v]
        if matches:
            return matches[0]
        else: # no continent found. This will happen for pseudo-countries
            return ('', set())
