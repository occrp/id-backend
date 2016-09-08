from __future__ import absolute_import

from jinja2 import Environment, Template
from django.utils.translation import to_locale, get_language
from django.core.urlresolvers import resolve, reverse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.messages import get_messages
from django.utils import translation, timesince, dateformat
from django.utils import formats
from django.conf import settings


EXTENSIONS = [
    'jinja2.ext.i18n',
    'jinja2.ext.with_',
    'pipeline.jinja2.PipelineExtension'
]


def get_verbose_or_field_name(field):
    # tries to get the verbose name of a model's field, and will
    # return just the field name upon failure
    try:
        return field.label.title()
    except:
        return field.name


def get_field_type(field):
    # returns the type of field ex. BooleanField, RadioField
    return field.field.widget.__class__.__name__


def get_widget_classes(field):
    # returns the extra classes defined in the widget
    # attributes of the form model
    try:
        return field.field.widget.attrs['class']
    except:
        print field.field.widget.attrs


def url_for(view, *args, **kwargs):
    return reverse(view, args=args, kwargs=kwargs)


def date_filter(date, format):
    if date is not None:
        return dateformat.format(date, format)
    return ''


class ContextTemplate(Template):

    def render(self, context):
        request = context.get('request')
        lang = get_language()
        if lang.startswith("en-"):
            lang = "en"
        if request is not None:
            context['user'] = request.user
            context['ROUTE_NAME'] = resolve(request.path_info).url_name

        context['LOCALE'] = to_locale(get_language())
        context['LOCALE_LC'] = to_locale(get_language()).lower()
        context['LANGUAGE_LC'] = lang.lower()
        context['LANGUAGES'] = settings.LANGUAGES
        short_format = formats.get_format("SHORT_DATE_FORMAT",
                                          lang=get_language())
        context['LANGUAGE_SHORT_DATE_FORMAT'] = short_format

        context['DEBUG'] = settings.DEBUG
        context['EMERGENCY'] = settings.EMERGENCY
        context['ID_SITE_NAME'] = settings.ID_SITE_NAME
        context['ID_VERSION'] = settings.ID_VERSION
        context['ID_FAVICON_URL'] = settings.ID_FAVICON_URL
        return super(ContextTemplate, self).render(context)


def environment(**options):
    env = Environment(extensions=EXTENSIONS, **options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url_for,
        'reverse': reverse,
        'get_messages': get_messages,
        'get_field_type': get_field_type,
        'get_widget_classes': get_widget_classes,
        'get_verbose_or_field_name': get_verbose_or_field_name
    })
    env.filters['timesince'] = timesince.timesince
    env.filters['date'] = date_filter
    env.template_class = ContextTemplate
    env.install_gettext_translations(translation)
    return env
