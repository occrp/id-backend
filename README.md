# The Investigative Dashboard Project API 🕵️

[![Translation status](https://hosted.weblate.org/widgets/occrp/-/investigative-dashboard/svg-badge.svg)](https://hosted.weblate.org/engage/occrp/?utm_source=widget)

[OCCRP](https://tech.occrp.org/projects/) research desk application API.

## Introduction

The ID is an ongoing project for many years. It started as a simple Django
web app and it was migrated to become a pure API with it's own SPA written
in Ember.js.

Both codebases are regularly updated and monitored for security
concerns. While making changes, it is important to keep in mind that this is
as much a security oriented project as it is functional.

The scope of this API is handle users authentication and securely serve the
API clients/SPA the data the users have access to. Users authentication is
handled via the Keycloak oAuth.

In order to ensure the email delivery, we also use a background processing
queue. This queue handles an automated weekly digest for active submissions.
The digest is an email with the breakdown of the user submissions/subscriptions.

### The Data Model

ID uses the standard Django user implementation under a `profile`.

The users get their roles based on their Keycloak role mappings. Some users
are mapped via the configuration file to receive notifications for new
submissions. A `staff` role user is allowed to triage/manage submissions and has
access to the reports.

The `ticket` is where the submissions are stored. A `ticket` has a requester
`profile` and is usually assigned a responder and there could be subscriber
`profiles`. The responder is the main submission researcher. Subscribers
can be attached to a `profile` or just a simple email address.

The `ticket` can represent one of the multiple kinds, eg. person, company, or
a simple data request. These kinds do not enforce a specific data model layout,
meaning that a ticket implements the idea of a _polymorphic_ data type.

The `ticket` allows `comments` and `attachments`. Both these create an `activity`
timeline.

The submission responder can add an `expense` to a ticket in order to keep
track of the payments required to provide a resolution. Once closed, there's
an automated email that is being sent to the `ticket` requester in order to
provide a `review` of the response they received.

Staff `profiles` can anytime access and export as CSVs, the `reviews`, along
with the `ticket` and the `expenses`. Staff has access to the stats for all of
these.

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
