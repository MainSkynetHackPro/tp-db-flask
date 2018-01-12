FROM ubuntu:16.04

RUN apt-get -y update

RUN apt-get install -y python3.5
RUN apt-get install -y python3-pip

RUN apt-get install -y postgresql-contrib-9.5

ADD requirements.txt ./tpdb/
ADD *.py ./tpdb/
ADD modules/ ./tpdb/modules
ADD models/ ./tpdb/models
ADD *.sh ./
ADD views/ ./tpdb/views
ADD schema.sql ./

RUN /usr/bin/pip3 install -r tpdb/requirements.txt

USER postgres
RUN /etc/init.d/postgresql start &&\
	psql --command "CREATE USER admin WITH SUPERUSER PASSWORD 'admin';" &&\
	createdb -E UTF8 -T template0 tpdb &&\
	psql tpdb --command "CREATE EXTENSION citext;" &&\
	/etc/init.d/postgresql stop

USER root

EXPOSE 5000

CMD /etc/init.d/postgresql start &&\
	/usr/bin/python3 tpdb/db_init.py &&\
	cd tpdb &&\
	gunicorn -w 4 forum:app --bind=0.0.0.0:5000
