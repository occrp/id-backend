# Investigative Dashboard v2
[![Codeship Status for occrp/investigative-dashboard-2](https://codeship.com/projects/634e8e20-a31d-0132-0304-366d28abf18c/status?branch=master)](https://codeship.com/projects/65925) [![Coverage Status](https://coveralls.io/repos/occrp/investigative-dashboard-2/badge.svg?branch=master)](https://coveralls.io/r/occrp/investigative-dashboard-2?branch=master)

Version 2 of the Investigative Dashboard.

## Databases

 * ElasticSearch for document storage.
 * Neo4j for graph storage.
 * MySQL for tickets and accounts.

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
 * [tpires/neo4j](https://registry.hub.docker.com/u/tpires/neo4j/)
 * [mysql](https://registry.hub.docker.com/_/mysql/)

Hence:

```
 docker pull tpires/neo4j
 docker pull mysql
```

Now go grab some coffee, this will take a while (depending on available bandwidth).

#### Set-up and run

Time to build Investigative Dashboard 2 image (you only have to do it once, or each time you modify the source). You can use any tagname for the image, just remember what you use (duh!). We're using `id2` tag here:
```
 docker build -t id2 /path/to/investigative-dashboard-2
```

After the build is complete, we can start running things. Run `mysql` (again, you can use whatever container name you feel like; we're using `id2-mysql` here):
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

Now, run `neo4j`:
```
 docker run -d \
   --name id2-neo4j \
   --cap-add SYS_RESOURCE \
   tpires/neo4j
```

Run Investigative Dashboard 2:
```
 docker run -d \
   --name id2 \
   --link id2-neo4j:neo4j \
   --link id2-mysql:mysql \
   --expose "8000" \
   id2
```

Check the IP addresses of `id2-neo4j` and `id2` containers:
```
 docker inspect -f '{{.NetworkSettings.IPAddress}}' id2-neo4j
 docker inspect -f '{{.NetworkSettings.IPAddress}}' id2
```

Fire up a browser and check if everything works by visiting `http://<id2-neo4j IP address>:7474/` and `http://<id2 IP address>:8000/`. You should see Neo4j's browser main page, and Investigative Dashboard's main page, respectively.

#### With docker-compose

Yes, you can use [docker-compose](http://docs.docker.com/compose/) to have all the images built, containers run and linked and `id2` started for you. Nice of you to ask. It's actually easier that way. **Caveat: you need at least docker 1.3 for that!**

```
 cd /path/to/investigative-dashboard-2
 docker-compose up
```

Get some info on the containers being run:
```
 $ ../docker-compose ps
             Name                            Command               State         Ports        
 ---------------------------------------------------------------------------------------------
 investigativedashboard2_id2_1     python manage.py runserver ...   Up      8000/tcp           
 investigativedashboard2_mysql_1   /entrypoint.sh mysqld            Up      3306/tcp           
 investigativedashboard2_neo4j_1   /bin/bash -c /launch.sh          Up      1337/tcp, 7474/tcp 
```

Check the IP addresses of `*_neo4j_` and `*_id2_*` (in the case above: `investigativedashboard2_neo4j_1`, `investigativedashboard2_id2_1`, respectively) containers:
```
 docker inspect -f '{{.NetworkSettings.IPAddress}}' investigativedashboard2_neo4j_1
 docker inspect -f '{{.NetworkSettings.IPAddress}}' investigativedashboard2_id2_1
```

Fire up a browser and check if everything works by visiting `http://<*_neo4j_* IP address>:7474/` and `http://*_id2_* IP address>:8000/`. You should see Neo4j's browser main page, and Investigative Dashboard's main page, respectively.

### Running locally

```
 ./manage.py runserver
```

## Data

Once the system is running, you can start [importing data](data/importers/ID1_Import/README.md).
