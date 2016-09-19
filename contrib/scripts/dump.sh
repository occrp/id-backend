#!/bin/bash

pg_dump -f /dumps/id2-`date +%d%m%Y%H%M%S`.sql $ID_DATABASE_URL
