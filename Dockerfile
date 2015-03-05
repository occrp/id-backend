FROM python:2.7.9

RUN mkdir -p /usr/src/id2
WORKDIR /usr/src/id2

COPY requirements.txt /usr/src/id2/
RUN pip install -r requirements.txt

COPY . /usr/src/id2/

VOLUME /data

RUN apt-get update && apt-get install -y \
		mysql-client libmysqlclient-dev \
		postgresql-client libpq-dev \
		sqlite3 \
		gcc \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
