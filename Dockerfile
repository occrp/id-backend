FROM node:slim
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

# you will need need these docker images too:
#  - postgres
# consult README.md for more information

RUN sed -i.bak 's/jessie main/jessie main non-free/g' /etc/apt/sources.list

RUN apt-get update && apt-get -y upgrade && apt-get -y dist-upgrade \
    && apt-get install -y -q --no-install-recommends unrar gcc \
        git libz-dev libjpeg-dev libfreetype6-dev python2.7 python-dev \
        python-pip postgresql-client-9.4 libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /id
WORKDIR /id/

# bower setup
RUN npm --quiet --silent install -g bower

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


# this can be volume-mounted
RUN mkdir -p /var/log/id2/
RUN chmod a+x /id/entrypoint.sh

ENTRYPOINT ["/id/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
