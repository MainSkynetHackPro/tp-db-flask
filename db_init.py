#!/usr/bin/env python
import psycopg2

import db_config


def db_init():
    connection = psycopg2.connect(dbname=db_config.name, user=db_config.user, password=db_config.password,
                                  host=db_config.host)
    cursor = connection.cursor()
    with open("schema.sql", 'r') as schema:
        cursor.execute(schema.read())
    connection.commit()
    cursor.close()
    connection.close()


db_init()
