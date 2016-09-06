FROM python:2.7.9

# you will need need these docker images too:
#  - postgres
# consult README.md for more information

RUN echo 'deb http://httpredir.debian.org/debian jessie non-free' > /etc/apt/sources.list.d/debian-non-free.list \
    && export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get -y upgrade && apt-get -y dist-upgrade && apt-get install -y \
    unrar gcc npm git libz-dev libjpeg-dev libfreetype6-dev python-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*
    #postgresql-client libpq-dev \
    #sqlite3 \

#RUN export DEBIAN_FRONTEND=noninteractive && apt-get -y autoremove

RUN mkdir -p /srv/tools/investigative-dashboard-2
WORKDIR /srv/tools/investigative-dashboard-2/

# python setup
RUN pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# bower setup
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install -g bower
# these are volume-mounted in development environments
COPY . /srv/tools/investigative-dashboard-2/
RUN chmod -R a+rX /srv/tools/investigative-dashboard-2/
RUN cd /srv/tools/investigative-dashboard-2/ && find ./ -iname '*.pyc' -exec rm -rf '{}' \;

# this can be volume-mounted
RUN mkdir -p /var/log/id2/

VOLUME ["/var/log/id2/"]

EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["/srv/tools/investigative-dashboard-2/docker.sh"]
