# Investigative Dashboard v2

Version 2 of the Investigative Dashboard.

## Databases

 * SQLite/MySQL/PostgreSQL for tickets and accounts.

## Testing

 * We use Codeship as our CI platform.
 * We're using Coveralls to monitor test coverage over time.

Manually run tests with:
```
 ./manage.py test
```

## Running

You can run `id2` either with `docker`, or standalone.

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
$ ssh root@woodward.occrp.org
$ cd /srv/tools/id/
$ git pull
$ git submodule update --init --recursive
$ docker-compose build # --no-cache
$ docker-compose up -d
$ # docker-compose logs -f
```

Static files are build upon ever run by the `entrypoint.sh` entrypoint script, since this needs to happen after volumes are mounted (so, runtime, not buildtime).

To see the logs:

```bash
$ ls /srv/logs/nginx/staging.occrp.org.*
$ ls /srv/logs/id2/
```

To see the backups:

```bash
$ ls /backups/woodward/(srv|dbs)/<date>
```

#### Daily email digests

To run daily email digests a cron installation or other schedule is required.

The command to run the digests is:

```cron
docker-compose run web python manage.py email_ticket_digest
```

It can also be triggered via a web request at:

```bash
$ curl http://investigativedashboard.org/api/v3/ops/email_ticket_digest
```

## Development accounts

When running in a development environment there are several debug users available.
To have these accounts set up, run:

```
 ./manage.py loaddata accounts/fixtures/*
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
