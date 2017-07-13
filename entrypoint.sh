#!/bin/bash

#
# this script is mainly here to handle static resources
echo "+-- handling static resources..."
cd /id/

echo "    +-- collectstatic..."
ID_SECRET_KEY=temp python manage.py collectstatic -v0 --noinput

echo "    +-- assets build..."
ID_SECRET_KEY=temp python manage.py assets -v0 build

echo "    +-- done."

echo "+-- running the command:"
echo "    $@"
exec "$@"