import psycopg2
import db_config


class DbConnector:
    connection = None
    cursor = None

    def __init__(self):
        pass

    def create_cursor(self):
        self.cursor = self.connection.cursor()

    def connect(self):
        self.connection = psycopg2.connect(
            dbname=db_config.name,
            user=db_config.user,
            password=db_config.password,
            host=db_config.host
        )
        self.create_cursor()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def execute(self, statement):
        self.connection()
        self.cursor.execute(statement=statement)
        return self.cursor.fetchall()
