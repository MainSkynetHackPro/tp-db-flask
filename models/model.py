from modules.dbconector import DbConnector
from modules.dbfield import DbField


class Model:
    tbl_name = 'base_model'

    def __init__(self):
        pass

    def create(self):
        sql = 'INSERT INTO "{0}" {1}'.format(self.tbl_name, self.get_sql_insert_fields())
        dbconnection = DbConnector()
        dbconnection.execute_set(sql)

    def edit(self):
        pass

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
        except IndexError:
            pass  # todo:found flag
        return self

    def delete(self):
        pass

    def load_from_array(self, array):
        for key in array:
            setattr(self, key, array[key])

    def load_from_json(self, json_payload):
        for key in json_payload:
            setattr(self, key, json_payload[key])

    @classmethod
    def get_sql_create(cls):
        def get_fields_sql(fields):
            sql = ""
            for i, item in enumerate(fields):
                if i < len(fields) - 1:
                    sql += '{0}{1}'.format(item.get_sql_create(), ',')
                else:
                    sql += item.get_sql_create()

            return sql

        sql = 'CREATE TABLE "{0}" ({1})'.format(getattr(cls, 'tbl_name'), get_fields_sql(cls.get_fields_list()))

        return sql

    @classmethod
    def get_fields_list(cls):
        fields = []
        for item in reversed(dir(cls)):
            if isinstance(getattr(cls, item), DbField):
                fields.append(getattr(cls, item))
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
