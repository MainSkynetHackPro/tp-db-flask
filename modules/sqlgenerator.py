from modules.dbconector import DbConnector


class SqlGenerator(object):
    TYPE_SELECT = 'select'
    TYPE_DELETE = 'delete'
    TYPE_UPDATE = 'update'
    TYPE_INSERT = 'insert'

    def __init__(self, tbl_name, query_type=TYPE_SELECT):
        self.__sql = ""
        self.tbl_name = tbl_name
        self.__where = {}
        self.__where_not = {}
        self.__type = query_type
        self.__update = {}
        self.__values = {}
        self.__or = {}

    def __get_sql_where(self):
        """
        Generates sql string WHERE field=value
        from self.where array
        {field: value,...}
        """
        sql = """ WHERE """
        for i, key in enumerate(self.__where):
            sql += """ "{0}" = '{1}'""".format(key, self.__where[key])
            if i < len(self.__where) - 1:
                sql += " AND "
        if len(self.__where) > 0 and len(self.__where_not) > 0:
            sql += " AND "
        for i, key in enumerate(self.__where_not):
            sql += """ "{0}" != '{1}'""".format(key, self.__where_not[key])
            if i < len(self.__where_not) - 1:
                sql += " AND "
        return sql

    def __get_sql_where_or(self):
        """
        Generates sql string WHERE field=value OR
        from self.where array
        {field: value,...}
        """
        sql = """ WHERE """
        for i, key in enumerate(self.__or):
            sql += """ "{0}" = '{1}'""".format(key, self.__or[key])
            if i < len(self.__or) - 1:
                sql += " OR "
        return sql

    def __get_sql_select(self):
        """
        Generates sql SELECT * FROM tbl_name
        :return: sql string
        """
        return """SELECT * FROM "{0}" """.format(self.tbl_name)

    def __get_sql_update(self):
        """
        Generates sql UPDATE tbl_name
        :return: sql string
        """
        return """UPDATE  "{0}" """.format(self.tbl_name)

    def __get_sql_insert(self):
        """
        Generates sql INSERT INTO tbl_name
        :return: sql string
        """
        return """INSERT INTO "{0}" """.format(self.tbl_name)

    def __get_sql_update_attributes(self):
        """
        Generates sql Update statement
        :return: sql string
        """
        sql = "SET "
        for i, key in enumerate(self.__update):
            sql += """"{0}" = '{1}'""".format(key, self.__update[key])
            if i < len(self.__update) - 1:
                sql += """, """
        return sql

    def __get_sql_insert_attributes(self):
        """
        Generates sql INSERT attributes
        :return: sql string
        """
        keys = ""
        values = ""
        for i, key in enumerate(self.__values):
            keys += """{0}""".format(key)
            values += """'{0}'""".format(self.__values[key])
            if i < len(self.__values) - 1:
                keys += """, """
                values += """, """
        return """ ({0}) VALUES ({1})""".format(keys, values)

    def __sql_query(self):
        """
        Generates full sql string with conditions
        :return: sql string
        """
        sql = ""
        if self.__type == self.TYPE_SELECT:
            sql = self.__get_sql_select()
        elif self.__type == self.TYPE_UPDATE:
            sql = self.__get_sql_update()
            sql += self.__get_sql_update_attributes()
        elif self.__type == self.TYPE_INSERT:
            sql = self.__get_sql_insert()
            sql += self.__get_sql_insert_attributes()
        if self.__where:
            sql += self.__get_sql_where()
        if self.__or:
            sql += self.__get_sql_where_or()
        return sql + ';'

    @staticmethod
    def safe_variable(variable):
        """
        safe to use variable
        :param variable:
        :return:
        """
        # todo: safe
        return variable

    def execute(self):
        """
        Executes sql string
        :return:  array {key: value,...}
        """
        sql = self.__sql_query()
        connector = DbConnector()
        if self.__type == self.TYPE_SELECT:
            data = connector.execute_get(sql)
            return data
        else:
            connector.execute_set(sql)
            return True

    def get_sql(self):
        """
        get formatted sql
        :return:
        """
        return self.__sql_query()

    def where(self, condition):
        """
        updates where condition
        :param condition:
        """
        self.__where.update(condition)

    def where_not(self, condition):
        """
        updates where NOT condition
        :param condition:
        """
        self.__where_not.update(condition)

    def where_or(self, condition):
        """
        updates where condition
        :param condition:
        """
        self.__or.update(condition)

    def update(self, condition):
        """
        updates fields to update condition
        :param condition:{field_to_update: updated_value}
        """
        self.__update.update(condition)

    def values(self, condition):
        """
        fills fields to insert condition
        :param condition:{field: value}
        """
        self.__values.update(condition)
