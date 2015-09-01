#!/bin/bash
#
# setting up and starting django app in docker
# includes executing makemigrations, migrate
#

echo -e '\n#####################################################################'
echo      '# migrate...'
echo      '#####################################################################'

# we want syncdb to run each time
python manage.py migrate
    
echo -e '\n#####################################################################'
echo      '# loading fixtures...'
echo      '#####################################################################'

python manage.py loaddata 'id/fixtures/initial_data.json'
        
 
echo -e '\n#####################################################################'
echo      '# running django...'
echo      '#####################################################################'

while true; do
    python manage.py runserver 0.0.0.0:8000
    sleep 5
    echo -e '\n#####################################################################'
    echo      '# restarting django...'
    echo      '#####################################################################'
done