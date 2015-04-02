#!/bin/bash
# maintainer: Michał "rysiek" Woźniak <rysiek@hackerspace.pl>
#

# Usage:
# ./bigtable-export.sh (--prod|--dev) <path-to-old-investigative-dashboard-source> <path-to-google-app-engine-sdk> <output-directory>

function be_help() {
  echo
  echo "Usage:"
  echo "  ./bigtable-export.sh (--prod|--dev) <path-to-old-investigative-dashboard-source> <path-to-google-app-engine-sdk> <output-directory>"
  echo
}

if [ -z "$1" ]; then
  echo 'Please identify the source environment (either `--prod`, or `--dev`) as the first argument.'
  be_help
  exit 1
elif [[ "$1" == "--dev" ]]; then
  ID_APP="s~investigative-dashboard-occrp"
  ID_APP_URL="https://investigative-dashboard-occrp.appspot.com"
elif [[ "$1" == "--prod" ]]; then
  ID_APP="s~investigative-dashboard-prod"
  ID_APP_URL="https://investigative-dashboard-prod.appspot.com"
elif [[ "$1" == "--help" ]]; then
  be_help
  exit 0
else
  echo "First argument is expected to be --prod, --dev, or --help"
  be_help
  exit 2
fi

if [ -z "$2" ]; then
  echo "Please supply the path to the sources of the old version of investigative dashboard as the second argument."
  be_help
  exit 3
fi

if [ -z "$3" ]; then
  echo "Please supply the path to Google App Engine SDK as the third argument."
  be_help
  exit 4
fi

if [ -z "$4" ]; then
  echo "Please supply the path to the output directory as the fourth argument."
  be_help
  exit 5
fi

ID_APP_DIR="$2"
APPENGINE_DIR="$3"
OUTPUT_DIR="$4"

# get user and password
read    -p 'AppEngine Email?    : ' APPENGINE_EMAIL
read -s -p 'AppEngine Password? : ' APPENGINE_PW

# can be: AccountRequest, UserProfile, TicketUpdate, Ticket
for DATA_KIND in AccountRequest UserProfile TicketUpdate Ticket; do
  echo "Exporting $DATA_KIND from $ID_APP..."
  OUTPUT_FILE="$OUTPUT_DIR/${DATA_KIND}.csv"

  mkdir -p "$OUTPUT_DIR"
  /usr/bin/env python2.7 "$APPENGINE_DIR/appcfg.py" download_data \
    --config_file="$ID_APP_DIR/bulkloader.yaml" \
    --filename="$OUTPUT_FILE" \
    --db_filename="$OUTPUT_FILE.progress.sql3" \
    --log_file="$OUTPUT_FILE.log" \
    --kind="$DATA_KIND" \
    --result_db_filename="$OUTPUT_FILE.result.db" \
    --url="$ID_APP_URL/_ah/remote_api" \
    --application="$ID_APP" \
    --batch_size=500 \
    --num_threads=50 \
    --bandwidth_limit=500000 \
    --email="$APPENGINE_EMAIL" \
    --rps_limit=1000 <<EOF
$APPENGINE_PW
$APPENGINE_PW
$APPENGINE_PW
$APPENGINE_PW
$APPENGINE_PW
EOF
  echo '...done.'
done