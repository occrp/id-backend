FROM python:2.7.9

# you will need need these docker images too:
#  - tpires/neo4j
#  - mysql
# consult README.md for more information

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y \
    mysql-client libmysqlclient-dev \
    gcc \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*
    #postgresql-client libpq-dev \
    #sqlite3 \

RUN export DEBIAN_FRONTEND=noninteractive && apt-get -y autoremove
    
RUN mkdir -p /usr/src/id2
WORKDIR /usr/src/id2

RUN pip install --upgrade pip
COPY requirements.txt /usr/src/id2/
RUN pip install -r requirements.txt

COPY . /usr/src/id2/
COPY ./settings/settings_local.py-docker /usr/src/id2/settings/settings_local.py
RUN mkdir -p /var/log/id2/

VOLUME /data

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
