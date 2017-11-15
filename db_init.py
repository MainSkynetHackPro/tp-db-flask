#!/usr/bin/env python
import psycopg2

import db_config


def get_sql_create():
    file = open('schema.sql', 'r')
    return file.read()


def db_init():
    connection = psycopg2.connect(dbname=db_config.name, user=db_config.user, password=db_config.password,
                                  host=db_config.host)
    cursor = connection.cursor()
    cursor.execute(get_sql_create())
    connection.commit()
    cursor.close()
    connection.close()


db_init()
