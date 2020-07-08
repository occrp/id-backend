# The Investigative Dashboard Project API 🕵️

[![Translation status](https://hosted.weblate.org/widgets/occrp/-/investigative-dashboard/svg-badge.svg)](https://hosted.weblate.org/engage/occrp/?utm_source=widget)

[OCCRP](https://tech.occrp.org/projects/) research desk application API.

# Prerequisites

- [Docker Compose](https://docs.docker.com/compose/install/)
- [ID Web App](https://git.occrp.org/libre/id-frontend) (optional)
- [InvestigativeDashboard.org homepage](https://git.occrp.org/libre/investigativedashboard.org)

# Setup

Please refer to the `id.env.tmpl` for the full list of settings.

Create a superuser to login to the admin:
```bash
$ docker-compose run --rm api ./manage.py createsuperuser
```

Start the dev server for local development or production:
```bash
$ docker-compose up
```

You might need to run migrations at times, to do that, run:
```bash
$ docker-compose run -e DJANGO_CONFIGURATION=Production api python manage.py migrate
```

Please see the `docker-compose.yml` for production ready deployments.

# Running the tests

To run the tests, use the `docker-compose.yml` configuration and run:
```bash
$ docker-compose run --rm api sh -c 'pip install -q --no-cache-dir -r requirements-testing.txt && flake8 && python manage.py test'
```

# Preparing a release

Before building the image set the version environment variable value:

```bash
$ export ID_VERSION=$(git describe --always)
```

## Enabling the daily digest

ID provides a daily digest email which can be executed and it will
self-schedule by running:

```
$ docker-compose run --rm api ./manage.py email_ticket_digest id.domain.tld --schedule=True
```

## Inspecting the queue

ID tasks use a little jobs queue. To see just the pending jobs in queue, run:
```
$ docker-compose run --rm api ./manage.py queue --inspect=False
```

To delete old processed jobs, run:
```
$ docker-compose run --rm api ./manage.py queue --clean=True
```

You're now ready to continuously ship! ✨ 💅 🛳
