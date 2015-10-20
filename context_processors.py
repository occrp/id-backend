# template context preprocessors
#
# as per:
# http://stackoverflow.com/questions/433162/can-i-access-constants-in-settings-py-from-templates-in-django#433255
#

from django.conf import settings # import the settings file

# debug, we might need it in the templates
def debug(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {
        'DEBUG': settings.DEBUG
    }