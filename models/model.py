from modules.dbconector import DbConnector
from modules.dbfield import DbField
from modules.sqlgenerator import SqlGenerator


class Model:
    tbl_name = 'base_model'
    exists = False
    serialize_fields = None

    def __init__(self):
        pass

    def __serialize(self):
        """
        serialize model
        :return: serialize model
        { field_name: value,...}
        """
        array = {}
        for field in self.__get_fields():
            if getattr(self, field).val():
                array[field] = getattr(self, field).val()
        return array

    def __get_fields(self):
        """
        return array of field names
        :return:
        [field_name,...]
        """
        fields = []
        for item in dir(self):
            if isinstance(getattr(self, item), DbField):
                fields.append(item)
        return fields

    def __get_pk_condition(self):
        """
        get pk key value
        :return:
        {pk_field: pk_value,...}
        """
        array = {}
        for item in dir(self):
            if isinstance(getattr(self, item), DbField) and getattr(self, item).is_pk():
                array[item] = getattr(self, item).val()
        return array

    def __deserialize(self, array):
        """
        deserialize model in array representation to model (fills fields)
        :param param: fetched array from SqlGenerator
        """
        for item, value in array.items():
            getattr(self, item).val(value)

    def create(self):
        """
        saves model to db
        """
        query = SqlGenerator(self.tbl_name, SqlGenerator.TYPE_INSERT)
        query.values(self.__serialize())
        query.execute()
        self.exists = True

    def update(self):
        """
        updates model by pk
        """
        query = SqlGenerator(self.tbl_name, SqlGenerator.TYPE_UPDATE)
        query.update(self.__serialize())
        query.where(self.__get_pk_condition())
        query.execute()

    def save(self):
        """
        updates or creates model based on self.exists
        """
        if self.exists:
            self.update()
        else:
            self.create()

    def get(self, params):
        """
        returns models list based on params
        :param params: where AND params
        {filed: value,...}
        :return:
        self for use like:
        model = Model().get({key:value})
        """
        query = SqlGenerator(self.tbl_name, SqlGenerator.TYPE_SELECT)
        query.where(params)
        query_data = query.execute()
        if query_data:
            self.__deserialize(query_data[0])
            self.exists = True
        return self

    def get_or(self, params):
        """
        returns models list based on params
        :param params: where OR params
        {filed: value,...}
        :return:
        self for use like:
        model = Model().get_or({key:value})
        """
        query = SqlGenerator(self.tbl_name, SqlGenerator.TYPE_SELECT)
        query.where_or(params)
        query_data = query.execute()
        if query_data:
            self.__deserialize(query_data[0])
            self.exists = True
        return self

    def get_list_or(self, params):
        """
        returns models list based on params
        :param params: where OR params
        {filed: value,...}
        :return:
        self for use like:
        model = Model().get_or({key:value})
        """
        query = SqlGenerator(self.tbl_name, SqlGenerator.TYPE_SELECT)
        query.where_or(params)
        return query.execute()

    @classmethod
    def serizlize_list(cls, list):
        """
        clean list by serialize_list values
        :param list:
        :return:
        list with allowed values
        """
        cleaned_list = []
        for item in list:
            item_array = {}
            for key, value in item.items():
                if key in cls.serialize_fields:
                    item_array[key] = value
            cleaned_list.append(item_array)
        return cleaned_list

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
            if isinstance(getattr(self, item), DbField) and self.serialize_fields and item in self.serialize_fields:
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
