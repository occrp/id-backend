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
 * tpires/neo4j
 * mysql

Hence:

```
 docker pull tpires/neo4j
 docker pull mysql
```

Now go grab some coffee, this will take a while depending on available bandwidth.

#### Set-up and run

Build Investigative Dashboard 2 image (you only have to do it once, or each time you modify the source); you can use any tagname for the image, just remember what you use (duh!):
```
 docker build -t ip2 /path/to/investigative-dashboard-2
```

Run `mysql`:
```
 
```

Run `neo4j`:
```
 
```

Run Investigative Dashboard 2:
```
 docker run ip2
```

#### With docker-compose

Yes, you can use [docker-compose](http://docs.docker.com/compose/) to have all the images built, containers run and linked and `ip2` started for you. Nice of you to ask. **Caveat: you need at least docker 1.3 for that!**

```
 cd /path/to/investigative-dashboard-2
 docker-compose up
```

### Running locally

```
 ./manage.py runserver
```

## Data

...
