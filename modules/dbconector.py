import psycopg2
import db_config

connection = psycopg2.connect(
    dbname=db_config.name,
    user=db_config.user,
    password=db_config.password,
    host=db_config.host
)


class DbConnector:
    @classmethod
    def connect(cls):
        return connection

    @classmethod
    def execute_get(cls, statement, variables=tuple()):
        connection = cls.connect()
        cursor = connection.cursor()
        cursor.execute(statement, variables)
        connection.commit()
        data = cls.get_datafield_array(cursor.fetchall(), cursor.description)
        cursor.close()
        return data

    @classmethod
    def execute_set(cls, statement, variables=tuple()):
        connection = cls.connect()
        cursor = connection.cursor()
        cursor.execute(statement, variables)
        connection.commit()
        cursor.close()

    @classmethod
    def execute_set_and_get(cls, statement, variables=tuple()):
        connection = cls.connect()
        cursor = connection.cursor()
        cursor.execute(statement, variables)
        connection.commit()
        data = cls.get_datafield_array(cursor.fetchall(), cursor.description)
        cursor.close()
        return data

    @classmethod
    def get_datafield_array(cls, fetched, description):
        datafield_set = []
        for fetch_item in fetched:
            datafield_item = {}
            for i, field in enumerate(description):
                datafield_item[field[0]] = fetch_item[i]
            datafield_set.append(datafield_item)
        return datafield_set
