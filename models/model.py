from modules.dbconector import DbConnector
from modules.dbfield import DbField


class Model:
    tbl_name = 'base_model'
    exists = False

    def __init__(self):
        pass

    def create(self):
        sql = 'INSERT INTO "{0}" {1}'.format(self.tbl_name, self.get_sql_insert_fields())
        dbconnection = DbConnector()
        dbconnection.execute_set(sql)
        self.exists = True

    def update(self):
        sql = """UPDATE "{0}" SET {1} WHERE {2}""".format(self.tbl_name, self.get_update_params(),
                                                          self.get_where_pk_params())
        dbconnection = DbConnector()
        dbconnection.execute_set(sql)

    def save(self):
        if self.exists:
            self.update()
        else:
            self.create()

    def get_update_params(self):
        update = {}
        for item in dir(self):
            if isinstance(getattr(self, item), DbField) and not getattr(self, item).is_pk():
                update[getattr(self, item).name] = getattr(self, item).val()

        sql = ""
        for i, key in enumerate(update):
            sql += """{0} = '{1}'""".format(key, update[key])
            if i < len(update) - 1:
                sql += """, """
        return sql

    def get_where_pk_params(self):
        where = {}
        for item in dir(self):
            if isinstance(getattr(self, item), DbField) and getattr(self, item).is_pk():
                where[getattr(self, item).name] = getattr(self, item).val()
        return self.get_where_params(where)

    def get_where_params(self, conditions):
        sql = ''
        for i, condition in enumerate(conditions):
            sql += "{0} = '{1}'".format(condition, conditions[condition])
            if i < len(conditions) - 1:
                sql += " AND "
        return sql

    def get(self, params):
        sql = 'SELECT * FROM "{0}" WHERE {1}'.format(self.tbl_name, self.get_where_params(params))
        dbconnection = DbConnector()
        try:
            datafield = dbconnection.execute_get(sql)[0]
            self.load_from_array(datafield)
            self.exists = True
        except IndexError:
            self.exists = False
        return self

    def delete(self):
        pass

    def load_from_array(self, array):
        for key in array:
            getattr(self, key).val(array[key])

    def load_from_json(self, json_payload):
        for key in json_payload:
            getattr(self, key).val(json_payload[key])

    def get_sql_create(self):
        def get_fields_sql(fields):
            sql = ""
            for i, item in enumerate(fields):
                if i < len(fields) - 1:
                    sql += '{0}{1}'.format(item.get_sql_create(), ',')
                else:
                    sql += item.get_sql_create()

            return sql

        sql = 'CREATE TABLE "{0}" ({1})'.format(getattr(self, 'tbl_name'), get_fields_sql(self.get_fields_list()))

        return sql

    def get_fields_list(self):
        fields = []
        for item in reversed(dir(self)):
            if isinstance(getattr(self, item), DbField):
                fields.append(getattr(self, item))
        return fields

    def serialize(self):
        array = {}
        for item in reversed(dir(self)):
            if isinstance(getattr(self, item), DbField):
                array[item] = getattr(self, item).val()
        return array

    def get_sql_insert_fields(self):
        keys = ""
        values = ""
        for i, item in enumerate(self.get_fields_list()):
            if item.value:
                keys += item.name
                if item.get_type() == "INT":
                    values += item.value
                else:
                    values += "'{0}'".format(item.value)
                if i < len(self.get_fields_list()) - 1:
                    keys += ", "
                    values += ", "
        return '({0}) VALUES ({1})'.format(keys, values)
