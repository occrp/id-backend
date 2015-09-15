#!/bin/bash
#
# setting up and starting django app in docker
# includes executing makemigrations, migrate
#

echo -e '\n#####################################################################'
echo      '# removing *.pyc...'
echo      '#####################################################################'

find ./ -iname '*.pyc' -exec rm -rf '{}' \;

if [ ! -e "settings/settings_local.py" ]; then
    echo -e '\n#####################################################################'
    echo      '# setting up settings_local.py from settings_local.py-docker'
    echo      '#####################################################################'
    
    cp -a settings/settings_local.py-docker settings/settings_local.py
fi

echo -e '\n#####################################################################'
echo      '# migrate...'
echo      '#####################################################################'

# we want migrate to run each time
while ! python manage.py migrate --noinput; do
    sleep 5
    echo -e '\n#####################################################################'
    echo      "# retrying migrations..."
    echo      '#####################################################################'
done

echo -e '\n#####################################################################'
if echo -ne 'from django.conf import settings\nprint settings.DEBUG\n\n' | python manage.py shell 2>/dev/null | grep True > /dev/null; then
    echo      '# DEBUG is True, loading fixtures...'
else
    echo      '# DEBUG is False, omitting fixtures...'
fi
echo      '#####################################################################'

python manage.py loaddata 'id/fixtures/initial_data.json'
        
# get the IP address
IP="$( ip -o -f inet a show dev eth0 | cut -d ' ' -f 7 | sed 's/\/.*//' )"
echo -e '\n#####################################################################'
echo      "# running django on $IP..."
echo      '#####################################################################'

while true; do
    python manage.py runserver 0.0.0.0:8000
    sleep 5
    echo -e '\n#####################################################################'
    echo      "# restarting django on $IP..."
    echo      '#####################################################################'
done