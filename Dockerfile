FROM ubuntu:16.04

RUN apt-get -y update

RUN apt-get install -y python3.5 python3-pip postgresql-contrib-9.5

ADD requirements.txt ./tpdb/
ADD *.py ./tpdb/
ADD modules/ ./tpdb/modules
ADD models/ ./tpdb/models
ADD *.sh ./
ADD views/ ./tpdb/views
ADD schema.sql ./

RUN /usr/bin/pip3 install -r tpdb/requirements.txt

RUN echo "listen_addresses='*'" >> /etc/postgresql/9.5/main/postgresql.conf &&\
     echo "synchronous_commit=off" >> /etc/postgresql/9.5/main/postgresql.conf &&\
     echo "shared_buffers = 512MB" >> /etc/postgresql/9.5/main/postgresql.conf &&\
     echo "effective_cache_size = 1024MB" >> /etc/postgresql/9.5/main/postgresql.conf &&\
     echo "wal_writer_delay = 2000ms" >> /etc/postgresql/9.5/main/postgresql.conf &&\
     echo "autovacuum = off" >> /etc/postgresql/9.5/main/postgresql.conf &&\
     echo "autovacuum = off" >> /etc/postgresql/9.5/main/postgresql.conf &&\
     echo "fsync = 'off'" >> /etc/postgresql/9.5/main/postgresql.conf

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
	gunicorn -w 8 forum:app --bind=0.0.0.0:5000
