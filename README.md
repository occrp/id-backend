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

### Running with Docker

You can run Investigative Dashboard under Docker. Here's how.

#### Prerequisites

Obviously, you'll need [Docker](http://docker.io/). [Go here](https://docs.docker.com/installation/#installation), ask questions later. For debian-based distros usually:

```
 apt-get install docker.io
```

Containers running these images are required prerequisites for running Inverstigative Dashboard 2:
 * [mysql](https://registry.hub.docker.com/_/mysql/) or [postgres](https://hub.docker.com/_/postgres/) (ignore if using SQLite)
 * [elasticsearch](https://hub.docker.com/_/elasticsearch/)

Hence:

```
 docker pull mysql # or postgres
 docker pull elasticsearch
```

Now go grab some coffee, this will take a while (depending on available bandwidth).

#### Set-up and run

Time to build Investigative Dashboard 2 image (you only have to do it once, or each time you modify the source). You can use any tagname for the image, just remember what you use (duh!). We're using `id2` tag here:
```
 docker build -t id2 /path/to/investigative-dashboard-2
```

After the build is complete, we can start running things. Run `mysql` or `postgres` (again, you can use whatever container name you feel like; we're using `id2-mysql` here):
```
 docker run -d \
   --name id2-mysql \
   -e MYSQL_ROOT_PASSWORD=root \
   -e MYSQL_USER=id2 \
   -e MYSQL_PASSWORD=id2 \
   -e MYSQL_DATABASE=id2 \
   mysql
```

**Credentials used above are just an example, do change them when running Investigative Dashboard 2 anywhere near an open Internet connection**, and once you do, remember to change them also in `settings/settings_local.py-docker` file!

Now, run `elasticsearch`:
```
 docker run -d \
   --name id2-elasticsearch \
   elasticsearch
```

Run Investigative Dashboard 2:
```
 docker run -d \
   --name id2 \
   --link id2-elasticsearch:elasticsearch \
   --link id2-mysql:mysql \
   --expose "8000" \
   id2
```

Check the IP addresses of and `id2` container:

```
 docker inspect -f '{{.NetworkSettings.IPAddress}}' id2
```

Fire up a browser and check if everything works by visiting `http://<id2 IP address>:8000/`. You should see Investigative Dashboard's main page.

#### With docker-compose

Yes, you can use [docker-compose](http://docs.docker.com/compose/) to have all the images built, containers run and linked and `id2` started for you. Nice of you to ask. It's actually easier that way. **Caveat: you need at least docker 1.3 for that!**

```
 cd /path/to/investigative-dashboard-2
 docker-compose up
```

Get some info on the containers being run:
```
 $ ../docker-compose ps
                    Name                                Command               State          Ports        
 -------------------------------------------------------------------------------------------------------
 investigativedashboard2_elasticsearch_1    /docker-entrypoint.sh elas ...   Up       9200/tcp, 9300/tcp 
 investigativedashboard2_id2_1              python manage.py runserver ...   Up       8000/tcp           
 investigativedashboard2_mysql_1            /entrypoint.sh mysqld            Up      3306/tcp           
```

Check the IP address of `*_id2_*` (in the case above: `investigativedashboard2_id2_1`) container:

```
 docker inspect -f '{{.NetworkSettings.IPAddress}}' investigativedashboard2_id2_1
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
