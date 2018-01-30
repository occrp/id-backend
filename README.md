# The Investigative Dashboard Project

[![Build Status](https://travis-ci.org/occrp/id-backend.svg?branch=master)](https://travis-ci.org/occrp/id-backend)
OCCRP research desk application. Check out the project's [documentation](http://occrp.github.io/id-backend/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)
- [Travis CLI](http://blog.travis-ci.com/2013-01-14-new-client/)

# Initialize the project

Create a superuser to login to the admin:

```bash
docker-compose run --rm web ./manage.py createsuperuser
```

Start the dev server for local development:
```bash
docker-compose up
```

# Preparing a release

To build the production-ready images run:

```bash
docker build --build-arg=ID_VERSION=$(git describe --always) -t occrp/id-backend ./
```

You're now ready to continuously ship! ✨ 💅 🛳
