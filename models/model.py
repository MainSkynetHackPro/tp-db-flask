from modules.dbfield import DbField
from modules.sqlgenerator import SqlGenerator


class Model:
    tbl_name = 'base_model'
    exists = False
    serialize_fields = '__all__'
    query = None

    def __init__(self):
        pass

    def __serialize(self, filter_fileds=False, use_alias=False):
        """
        serialize model
        :input: user_alias - returns serialised by model alias if exists
        filter_fields - returns allowed fields from self.serialize_fields
        :return: serialize model
        { field_name: value,...}
        """
        array = {}
        for field in self.get_fields_names_list():
            if getattr(self, field).val() is not None:
                if not filter_fileds or filter_fileds and (
                        self.serialize_fields == '__all__' or field in self.serialize_fields):
                    if use_alias:
                        array[getattr(self, field).alias] = str(getattr(self, field).val())
                    else:
                        array[field] = str(getattr(self, field).val())
        return array

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

    @classmethod
    def get_sql_generator(cls, type):
        """
        returns sql generator for select
        :return:
        """
        types = (SqlGenerator.TYPE_SELECT, SqlGenerator.TYPE_UPDATE, SqlGenerator.TYPE_INSERT, SqlGenerator.TYPE_DELETE)
        if type not in types:
            raise Exception("Not allowed type")
        return SqlGenerator(cls.tbl_name, type)

    def load_from_dict(self, dict):
        """
        loads data from dict
        :param dict:
        """
        fields = self.get_fields_names_list()
        for key in dict:
            if key in fields:
                getattr(self, key).val(dict[key])

    def load_from_json(self, json_payload):
        """
        loads data from parsed json
        :param json_payload:
        """
        fields = self.get_fields_names_list()
        for key in json_payload:
            if key in fields:
                getattr(self, key).val(json_payload[key])

    def get_sql_create(self):
        """
        get model sql code
        :return:
        """
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
        """
        get fields list
        [DbField,...]
        """
        fields = []
        for item in reversed(dir(self)):
            if isinstance(getattr(self, item), DbField):
                fields.append(getattr(self, item))
        return fields

    def get_fields_names_list(self):
        """
        get fields names list
        [field_name,...]
        """
        fields = []
        for item in reversed(dir(self)):
            if isinstance(getattr(self, item), DbField):
                fields.append(item)
        return fields

    def serialize(self, use_alias=False):
        """
        get serialised model
        :param use_alias: return field alias name
        :return: dict {field: value,...}
        """
        return self.__serialize(filter_fileds=True, use_alias=use_alias)