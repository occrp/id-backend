FROM python:2.7.9

# you will need need these docker images too:
#  - tpires/neo4j
#  - mysql
# consult README.md for more information

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y \
    mysql-client libmysqlclient-dev \
    gcc \
    npm \
    git \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*
    #postgresql-client libpq-dev \
    #sqlite3 \

#RUN export DEBIAN_FRONTEND=noninteractive && apt-get -y autoremove
    
RUN mkdir -p /usr/src/id2
WORKDIR /usr/src/id2

# python setup
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/id2/
RUN pip install -r requirements.txt

# bower setup
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install -g bower

# these are volume-mounted now
COPY . /usr/src/id2/
RUN rm /usr/src/id2/settings/settings_local.py /usr/src/id2/settings/settings_local.pyc
RUN cd /usr/src/id2/ && find ./ -iname '*.pyc' -exec rm -rf '{}' \;
#COPY ./settings/settings_local.py-docker /usr/src/id2/settings/settings_local.py

# bower static resources setup
RUN cd static/ && bower --allow-root install
RUN npm uninstall bower
RUN export DEBIAN_FRONTEND=noninteractive && apt-get -y purge npm nodejs git && apt-get -y autoremove && rm /usr/bin/node

# this can be volume-mounted
RUN mkdir -p /var/log/id2/

EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["/usr/src/id2/docker.sh"]
