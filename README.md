# Investigative Dashboard Project

[![Build Status](https://travis-ci.org/occrp/id-backend.svg?branch=master)](https://travis-ci.org/occrp/id-backend)

This is our research desk ticket software.

## Testing

Manually run tests with:
```
 ./manage.py test
```

## Running

You can run the project either with `docker`, or standalone.

Before you begin, copy the `id.env.tmpl` file and edit the settings in it.

This files is used by Docker, in order to run the application locally,
you will have to export the settings to environment variables manually.

If you are running the application for the first time, you will need to
run the migrations:
```
python manage.py migrate
```

Now you can start the application:

```
 ./manage.py runserver
```

### In Production

At this moment, there's no automated deployments.
Please consider the steps below:

```bash
$ (your-production-server) git pull
$ (your-production-server) git submodule update --init --recursive
$ (your-production-server) docker-compose build # --no-cache
$ (your-production-server) docker-compose up -d
$ (your-production-server) # docker-compose logs -f
```

Static files are build upon ever run by the Docker *entrypoint* script,
since this needs to happen after volumes are mounted.

#### Daily email digests

To run daily email digests a cron installation or other schedule is required.

The command to run the digests is:

```cron
docker-compose run web python manage.py email_ticket_digest
```

It can also be triggered via a web request at:

```bash
$ curl https://your-id-host.tld/api/v3/ops/email_ticket_digest
```
