FROM python:2-alpine

RUN apk add --no-cache build-base postgresql-dev

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Adds our application code to the image
COPY . /id/
WORKDIR /id/

EXPOSE 8000

ARG ID_VERSION=0.0.0-x
ENV ID_VERSION=$ID_VERSION

LABEL VERSION=$ID_VERSION

CMD gunicorn --bind 0.0.0.0:$PORT  --log-file - api_v3.wsgi:application
