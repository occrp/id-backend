# -*- coding: utf-8 -*-

import os
import django
from django.core.management import call_command

print('\n%s' % ('#'*70))
print('# django setup...')
print('#'*70)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
django.setup()

# because reasons:
# https://code.djangoproject.com/ticket/8085
if not os.environ.get('RUN_MAIN', False):

    print('\n%s' % ('#'*70))
    print('# syncdb...')
    print('#'*70)
    
    # we want syncdb to run each time
    call_command('syncdb', interactive=False)

# load debugging fixtures if we're in debug mode
if django.conf.settings.DEBUG:
    print('\n%s' % ('#'*70))
    print('# loading fixtures...')
    print('#'*70)
    call_command('loaddata', 'id/fixtures/initial_data.json')
        
 
print('\n%s' % ('#'*70))
print('# running django...')
print('#'*70)

call_command('runserver', '0.0.0.0:8000')