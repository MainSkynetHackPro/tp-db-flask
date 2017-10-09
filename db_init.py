#!/usr/bin/env python
import psycopg2


def db_init():
    connection = psycopg2.connect(dbname="tpdb", user="admin", password="admin", host="localhost")
    cursor = connection.cursor()
    with open("schema.sql", 'r') as schema:
        cursor.execute(schema.read())
    connection.commit()
    cursor.close()
    connection.close()


db_init()
