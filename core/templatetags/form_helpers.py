from django_jinja import library
from core.utils import version


@library.global_function
def get_verbose_or_field_name(field):
    # tries to get the verbose name of a model's field, and will
    # return just the field name upon failure
    try:
        return field.label.title()
    except:
        return field.name


@library.global_function
def get_field_type(field):
    # returns the type of field ex. BooleanField, RadioField
    return field.field.widget.__class__.__name__


@library.global_function
def get_widget_classes(field):
    # returns the extra classes defined in the widget attributes of the form model
    try:
        return field.field.widget.attrs['class']
    except:
        print field.field.widget.attrs


@library.global_function
def id_version():
    return version()
