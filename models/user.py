from models.dbmodel import DbModel
from modules.dbconector import DbConnector


class User(DbModel):
    tbl_name = "tbl_user"

    def sql_select(self, hide_id=True):
        additional = ""
        if not hide_id:
            additional = "{0}.id, ".format(self.tbl_name)
        return """
            SELECT 
              {additional}
              {tbl_name}.nickname,
              {tbl_name}.fullname,
              {tbl_name}.email,
              {tbl_name}.about
            FROM {tbl_name}
        """.format(**{'additional': additional, 'tbl_name': self.tbl_name})

    def sql_insert_returning(self, sql):
        return """
            {sql_insert}
            RETURNING nickname, fullname, email, about
        """.format(**{'sql_insert': sql})

    def sql_where_nickname_or_email(self, nickname, email):
        return """
            WHERE 
              LOWER({tbl_name}.nickname) = LOWER('{nickname}') OR
              LOWER({tbl_name}.email) = LOWER('{email}')
        """.format(**{'tbl_name': self.tbl_name, 'nickname': nickname, 'email': email})

    def sql_where_nickname(self, nickname):
        return """
            WHERE 
              LOWER({tbl_name}.nickname) = LOWER('{nickname}')
        """.format(**{'tbl_name': self.tbl_name, 'nickname': nickname,})

    def sql_others_nickname_or_email(self, user_id, nickname, email):
        return """
            WHERE 
              (LOWER({tbl_name}.nickname) = LOWER('{nickname}') OR
              LOWER({tbl_name}.email) = LOWER('{email}')) AND
              {tbl_name}.id != {id}
        """.format(**{'tbl_name': self.tbl_name, 'nickname': nickname, 'email': email, 'id': user_id})

    def create_by_nickname(self, nickname, payload):
        user = self.get_all_by_nickname_or_email(nickname, payload['email'])
        if user:
            return user, self.EXISTS
        payload['nickname'] = nickname
        sql = self.sql_insert(fields=payload)
        user = DbConnector().execute_set_and_get(self.sql_insert_returning(sql))
        return user[0], self.CREATED

    def get_all_by_nickname_or_email(self, nickname, email):
        sql = self.sql_builder(self.sql_select(), self.sql_where_nickname_or_email(nickname, email))
        return DbConnector().execute_get(sql)

    def get_by_nickname(self, nickname, hide_id=True):
        sql = self.sql_builder(self.sql_select(hide_id=hide_id), self.sql_where_nickname(nickname))
        data = DbConnector().execute_get(sql)
        return data[0] if data else {}

    def update_by_nickname(self, nickname, payload):
        if not payload:
            user = self.get_by_nickname(nickname)
            if user:
                return user, self.FOUND
            return {}, self.NOT_FOUND
        user = self.get_by_nickname(nickname, hide_id=False)
        if not user:
            return {}, self.NOT_FOUND
        user_id = user['id']
        user = self.find_others_with_nickname_or_email(
            user_id,
            payload['nickname'] if 'nickname' in payload else None,
            payload['email'] if 'email' in payload else None
        )
        if user:
            return user, self.CONFLICTS
        user = self.update_by_id(user_id, payload)
        return user, self.FOUND

    def get_others_with_nickname_or_email(self, user_id, nickname, email):
        sql = self.sql_builder(self.sql_select(), self.sql_others_nickname_or_email(user_id, nickname, email))
        return DbConnector().execute_get(sql)

    def update_by_id(self, id, payload):
        update = ''
        counter = len(payload)
        for key, value in payload.items():
            counter -= 1
            update += " {0} = '{1}'".format(key, value)
            if counter > 0:
                update += ","
        sql = """
            UPDATE {tbl_name} SET
              {update_str}
            WHERE id = {id}
            RETURNING nickname, fullname, email, about
        """.format(**{
            'tbl_name': self.tbl_name,
            'id': id,
            'update_str': update
        })

        return DbConnector().execute_set_and_get(sql)[0]

    def find_others_with_nickname_or_email(self, user_id, nickname, email):
        if not (nickname or email):
            return []
        where_condition = ''
        if nickname:
            where_condition += "LOWER({tbl_name}.nickname) = LOWER('{nickname}')".format(**{'tbl_name': self.tbl_name, 'nickname': nickname})
        if email:
            where_condition += "{or} LOWER({tbl_name}.email) = LOWER('{email}')".format(**{
                'or': 'OR' if where_condition else '',
                'tbl_name': self.tbl_name,
                'email': email
            })
        where_condition = "WHERE ({where}) AND {tbl_name}.id != {id}".format(**{
            'where': where_condition,
            'tbl_name': self.tbl_name,
            'id': user_id
        })
        data = DbConnector().execute_get(self.sql_builder(self.sql_select(), where_condition))
        return data[0] if data else []



