from modules.dbfield import DbField


class Model:
    tbl_name = 'base_model'

    def __init__(self):
        pass

    def create(self):
        pass

    def edit(self):
        pass

    def get(self):
        pass

    def delete(self):
        pass

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
