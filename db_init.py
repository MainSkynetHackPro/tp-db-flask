#!/usr/bin/env python
import psycopg2

import db_config
from models.user import User


# def db_init():
#     connection = psycopg2.connect(dbname=db_config.name, user=db_config.user, password=db_config.password,
#                                   host=db_config.host)
#     cursor = connection.cursor()
#     with open("schema.sql", 'r') as schema:
#         cursor.execute(schema.read())
#     connection.commit()
#     cursor.close()
#     connection.close()

def db_init():
    connection = psycopg2.connect(dbname=db_config.name, user=db_config.user, password=db_config.password,
                                  host=db_config.host)
    cursor = connection.cursor()
    cursor.execute(db_create_sql())
    connection.commit()
    cursor.close()
    connection.close()


def db_create_sql():
    models = (User,)
    create_sql = ''
    for model in models:
        create_sql += 'DROP TABLE IF EXISTS "{0}";'.format(getattr(model, 'tbl_name'))
        create_sql += model.get_sql_create()
    sql_file = open('_tmp_sql/db.sql', 'w')
    sql_file.write(create_sql)
    sql_file.close()
    return create_sql


db_init()
