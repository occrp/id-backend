from __future__ import absolute_import

from jinja2 import Environment, Template
from django_assets.env import get_env
from django.template import RequestContext
from django.utils.translation import to_locale, get_language, activate
from django.core.urlresolvers import resolve, reverse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.messages import get_messages
from django.contrib.humanize.templatetags import humanize
from django.utils import translation, timesince, dateformat
from django.utils import formats
from django.conf import settings


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


def intcomma_filter(source, use_l10n=True):
    return humanize.intcomma(source, use_l10n)


class ContextTemplate(Template):

    def render(self, context):
        request = context.get('request')
        context['DEBUG'] = settings.DEBUG

        if request is not None:
            context['user'] = request.user
            context['ROUTE_NAME'] = resolve(request.path_info).url_name

        lang = get_language()
        if not lang or lang.startswith("en-"):
            lang = "en"
        activate(lang)
        context['LOCALE'] = to_locale(get_language())
        context['LOCALE_LC'] = to_locale(get_language()).lower()
        context['LANGUAGE_LC'] = lang.lower()
        context['LANGUAGES'] = settings.LANGUAGES
        short_format = formats.get_format("SHORT_DATE_FORMAT",
                                          lang=get_language())
        context['LANGUAGE_SHORT_DATE_FORMAT'] = short_format
        context['EMERGENCY'] = settings.EMERGENCY
        context['ID_SITE_NAME'] = settings.ID_SITE_NAME
        context['ID_VERSION'] = settings.ID_VERSION
        context['ID_FAVICON_URL'] = settings.ID_FAVICON_URL
        context['ALEPH_URL'] = settings.ALEPH_URL

        # FIXME DEBUG
        if isinstance(context, RequestContext):
            context = dict(context.flatten())

        return super(ContextTemplate, self).render(context)


def environment(**options):
    env = Environment(extensions=settings.JINJA2_EXTENSIONS, **options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url_for,
        'reverse': reverse,
        'get_messages': get_messages,
        'get_field_type': get_field_type,
        'get_widget_classes': get_widget_classes,
        'get_verbose_or_field_name': get_verbose_or_field_name
    })
    env.assets_environment = get_env()
    env.filters['timesince'] = timesince.timesince
    env.filters['date'] = date_filter
    env.filters['intcomma'] = intcomma_filter
    env.template_class = ContextTemplate
    env.install_gettext_translations(translation)
    return env
