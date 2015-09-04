#!/bin/bash
#
# setting up and starting django app in docker
# includes executing makemigrations, migrate
#

echo -e '\n#####################################################################'
echo      '# removing *.pyc...'
echo      '#####################################################################'

find ./ -iname '*.pyc' -exec rm -rf '{}' \;

echo -e '\n#####################################################################'
echo      '# migrate...'
echo      '#####################################################################'

# we want migrate to run each time
python manage.py migrate --noinput
    
echo -e '\n#####################################################################'
echo      '# loading fixtures...'
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