import abc


class DbModel:
    FOUND = 200
    CREATED = 201
    NOT_FOUND = 404
    EXISTS = 409
    CONFLICTS = 409
    tbl_name = None

    def sql_builder(self, *args):
        sql = ""
        for arg in args:
            sql += "{0} ".format(arg)
        return sql

    def sql_select(self, hide_id=True):
        """
        get sql select statement
        SELECT
            field,
            field...
        FROM ...
        JOIN if needed
        :return:
        """
        return

    def sql_where(self, fields):
        """
        returns sql where statement
        :param fields:
        :return:
        """
        sql = "WHERE "
        for field, value in fields.items():
            sql += "{0}='{1}'".format(field, value)
        return sql

    def sql_insert(self, fields):
        keys = ""
        values = ""
        count = len(fields)
        for field, value in fields.items():
            count -= 1
            keys += " {0}".format(field)
            values += " '{0}'".format(value)
            if count > 0:
                keys += ","
                values += ","
        return """INSERT INTO {0} ({1}) VALUES ({2})""".format(self.tbl_name, keys, values)
