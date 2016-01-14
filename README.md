# Investigative Dashboard v2
[![Codeship Status for occrp/investigative-dashboard-2](https://codeship.com/projects/634e8e20-a31d-0132-0304-366d28abf18c/status?branch=master)](https://codeship.com/projects/65925) [![Coverage Status](https://coveralls.io/repos/occrp/investigative-dashboard-2/badge.svg?branch=master)](https://coveralls.io/r/occrp/investigative-dashboard-2?branch=master)

Version 2 of the Investigative Dashboard.

## Databases

 * SQLite/MySQL/PostgreSQL for tickets and accounts.
 * ElasticSearch for document storage.

## Testing

 * We use Codeship as our CI platform.
 * We're using Coveralls to monitor test coverage over time.

Manually run tests with:
```
 ./manage.py test
```

## Running

You can run `id2` eitehr with `docker`, or standalone.

### Running with Docker and Docker Compose

You can run Investigative Dashboard under Docker. Here's how.

#### Prerequisites

Obviously, you'll need [Docker](http://docker.io/). [Go here](https://docs.docker.com/installation/#installation), ask questions later. For debian-based distros usually:

```
 apt-get install docker.io
```

Also, if setting up for production use (i.e. not volume-mounting the code directory in the container, but rather relying on the code COPY'ed at build time; and running as non-root user within the container), **remember to `chmod -R a+rX ./` in the code directory before build** -- otherwise on some `docker` or `aufs` versions the permissions might be broken within the container which will cause `id2` not to run.

#### Set-up and run with docker-compose

You should use [docker-compose](http://docs.docker.com/compose/) to have all the images built, containers run and linked and `id2` started for you. Nice of you to ask. It's actually easier that way. **Caveat: you need at least docker 1.3 for that!**

**CAVEAT:** Before you do so, edit the `settings/settings_local.py-docker` file and set `DEBUG` to `True`!

```
 cd /path/to/investigative-dashboard-2
 docker-compose up id2dev
```

Get some info on the containers being run:
```
 $ ../docker-compose ps
                    Name                                Command               State          Ports        
 -------------------------------------------------------------------------------------------------------
 investigativedashboard2_elasticsearch_1    /docker-entrypoint.sh elas ...   Up       9200/tcp, 9300/tcp 
 investigativedashboard2_id2_1              python manage.py runserver ...   Up       8000/tcp
 investigativedashboard2_postgres_1         /docker-entrypoint.sh postgres   Up       5432/tcp
```

Check the IP address of `*_id2_*` (in the case above: `investigativedashboard2_id2_1`) container:

```
 docker inspect -f '{{.NetworkSettings.IPAddress}}' investigativedashboard2_id2dev_1
```

Fire up a browser and check if everything works by visiting `http://*_id2_* IP address>:8000/`. You should see Investigative Dashboard's main page.

### Running locally

```
 ./manage.py runserver
```

## Development accounts

When running in a development environment there are several debug users available. To have these accounts set up, run:

```
 ./manage.py loaddata id/fixtures/*
```

**Do not run this in production!!**

Development/debug user accounts are:
 - `nonuser@example.com` : `asdf`
 - `nuser@example.com` : `asdf`
 - `volunteer@example.com` : `asdf`
 - `staff@example.com` : `asdf`
 - `admin@example.com` : `asdf`


## Data

Once the system is running, you can start [importing data](data/importers/README.md).
