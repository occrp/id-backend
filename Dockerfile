FROM python:2-alpine
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --virtual .build-deps \
  build-base postgresql-dev

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Adds our application code to the image
COPY . /id/
WORKDIR /id/

EXPOSE 8000

CMD gunicorn --bind 0.0.0.0:$PORT  --log-file - api_v3.wsgi:application
