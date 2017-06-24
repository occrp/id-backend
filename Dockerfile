FROM python:2.7.10
ENV DEBIAN_FRONTEND noninteractive

# you will need need these docker images too:
#  - postgres
# consult README.md for more information

RUN echo 'deb http://httpredir.debian.org/debian jessie non-free' > /etc/apt/sources.list.d/debian-non-free.list
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get update && apt-get -y upgrade && apt-get -y dist-upgrade \
    && apt-get install -y -q --no-install-recommends unrar gcc nodejs \
        git libz-dev libjpeg-dev libfreetype6-dev python-dev gunicorn \
        postgresql-client-9.4 ruby-sass \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /id
WORKDIR /id/

# bower setup
RUN npm --quiet --silent install -g bower uglifyjs

# python setup
RUN pip install -q --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -q -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY package.json /id
RUN cd /id && npm install --unsafe-perm

# these are volume-mounted in development environments
COPY . /id/
RUN chmod -R a+rX /id/
# && pip install -e /id
RUN cd /id/static && bower --allow-root --quiet --config.interactive=false --force install
RUN ID_SECRET_KEY=temp python manage.py collectstatic --noinput


# this can be volume-mounted
RUN mkdir -p /var/log/id2/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["/id/docker.sh"]
