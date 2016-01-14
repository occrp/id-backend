#!/bin/bash
#
# setting up and starting django app in docker
# includes executing makemigrations, migrate
#

function abort {
    echo
    echo "* * * ABORTED! * * *"
    echo
    exit 0
}

trap "abort" SIGKILL SIGTERM STOP SIGHUP SIGINT EXIT

echo -e '\n#####################################################################'
echo      '# removing *.pyc...'
echo      '#####################################################################'

find ./ -iname '*.pyc' -exec rm -rf '{}' \;

echo -e '\n#####################################################################'
echo      '# doing a bower install run...'
echo      '#####################################################################'

cd ./static/
# we need --allow-root for when this is actually run as root (which should *not* happen in production!)
# and we need GIT_DIR=/tmp/ because otherwise when run as a different user than the one that owns ~/.git/config
# git will fails, and take bower with it
GIT_DIR=/tmp/ bower --allow-root --config.interactive=false --verbose --force install
cd ../


echo -e '\n#####################################################################'
echo      '# make sure elasticsearch is running...'
echo      '#####################################################################'

echo 'waiting max 60s for elasticsearch...'

CURLS=60
while ! curl -s --max-time 1 -I http://elasticsearch:9200/ | grep 'HTTP/1.1 200 OK' > /dev/null; do
    echo -n '.'
    CURLS=$((CURLS-1))
    if [[ $CURLS == 0 ]]; then
        echo 'failed!'
        echo
        echo '* * * ERROR: cannot connect to elasticsearch! * * *'
        echo
        exit 1
    fi
    sleep 1
done
echo 'elasticsearch is up.'


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

echo -ne 'from django.conf import settings\nprint settings.DEBUG\n\n' | python manage.py shell 2>/dev/null | grep True > /dev/null 
DEBUG=$?

# root permitted only in debug mode
if [ `whoami` = "root" ] && [ $DEBUG != 0 ]; then
    echo
    echo "ERROR: running as root, but DEBUG is false, aborting!"
    echo
    abort
fi

echo -e '\n#####################################################################'
# 0 is "true" in UNIX/bash world
if [ $DEBUG -eq 0 ]; then
    echo      '# DEBUG is True, loading fixtures...'
    python manage.py loaddata 'id/fixtures/initial_data.json'
    
else
    echo      '# DEBUG is False, omitting fixtures...'
fi
echo      '#####################################################################'


# get the IP address
IP="$( ip -o -f inet a show dev eth0 | cut -d ' ' -f 7 | sed 's/\/.*//' )"
echo -e '\n#####################################################################'

if [ $DEBUG -eq 0 ]; then
    echo      "# running debug django (runserver) on $IP..."
else
    echo      "# running production django (runfcgi) on $IP..."
fi
echo      '#####################################################################'

while true; do
    if [ $DEBUG -eq 0 ]; then
        python manage.py runserver 0.0.0.0:8000
    else
        python manage.py runfcgi method=prefork host=0.0.0.0 port=8000 daemonize=false
    fi
    
    sleep 5
    echo -e '\n#####################################################################'
    if [ $DEBUG -eq 0 ]; then
        echo      "# restarting debug django (runserver) on $IP..."
    else
        echo      "# restarting production django (runfcgi) on $IP..."
    fi
    echo      '#####################################################################'
done