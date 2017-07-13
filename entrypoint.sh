#!/bin/bash

#
# this script is mainly here to handle static resources
echo "+-- handling static resources..."
cd /id/
echo "    +-- collectstatic..."
python manage.py collectstatic
echo "    +-- assets build..."
python manage.py assets build
echo "    +-- done."
echo "+-- running the command:"
echo "    $@"
exec "$@"