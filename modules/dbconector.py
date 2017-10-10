import psycopg2
import db_config


class DbConnector:
    connection = None
    cursor = None

    def __init__(self):
        self.connect()

    def __del__(self):
        self.disconnect()

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

    def execute_get(self, statement):
        self.cursor.execute(statement)
        return self.get_datafield_array(self.cursor.fetchall(), self.cursor.description)

    def execute_set(self, statement):
        self.cursor.execute(statement)
        self.connection.commit()

    def get_datafield_array(self, fetched, description):
        datafield_set = []
        for fetch_item in fetched:
            datafield_item = {}
            for i, field in enumerate(description):
                datafield_item[field[0]] = fetch_item[i]
            datafield_set.append(datafield_item)
        return datafield_set
