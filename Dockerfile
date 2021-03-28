FROM python:3.9-alpine

RUN apk add --no-cache libffi-dev build-base postgresql-dev rust cargo

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Adds our application code to the image
COPY . /id/
WORKDIR /id/

EXPOSE 8080

ARG ID_VERSION=0.0.0-x
ENV ID_VERSION=$ID_VERSION

LABEL VERSION=$ID_VERSION

CMD gunicorn --bind 0.0.0.0:8080  --log-file - api_v3.wsgi:application
