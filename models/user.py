from models.model import Model
from modules.dbconector import DbConnector
from modules.dbfield import DbField
from modules.sqlgenerator import SqlGenerator


class User(Model):
    tbl_name = 'user'

    serialize_fields = ('nickname', 'fullname', 'email', 'about')

    def __init__(self):
        self.id = DbField(name='id', type='SERIAL', primary_key=True)
        self.nickname = DbField(name='nickname', type='VARCHAR(25)', primary_key=False)
        self.fullname = DbField(name='fullname', type='VARCHAR(25)', primary_key=False)
        self.email = DbField(name='email', type='VARCHAR(25)', primary_key=False)
        self.about = DbField(name='about', type='VARCHAR(128)', primary_key=False)
        super().__init__()

    @classmethod
    def get_users_with_nickname_or_email(cls, nickname, email):
        sql = """
            SELECT *
            FROM "user"
            WHERE LOWER(nickname) = LOWER('{0}')
                  OR LOWER(email) = LOWER('{1}')
        """.format(
            SqlGenerator.safe_variable(nickname),
            SqlGenerator.safe_variable(email)
        )

        return DbConnector().execute_get(sql)

    @classmethod
    def get_user_by_nickname(cls, nickname, hide_id=True):
        sql = """
                    SELECT 
                      {0}
                      about,
                      email,
                      nickname,
                      fullname
                    FROM "user"
                    WHERE LOWER(nickname) = LOWER('{1}')
                """.format(
            'id, ' if not hide_id else '',
            SqlGenerator.safe_variable(nickname),
        )
        user = DbConnector().execute_get(sql)
        if user:
            return user[0]
        else:
            return None

    @classmethod
    def get_users_by_or_attributes(cls, params):
        sql = """
                    SELECT *
                    FROM "user" 
                """
        or_param = False
        for param in params:
            if or_param:
                sql += " OR "
            else:
                sql += " WHERE "
            sql += """LOWER({0}) = LOWER('{1}')""".format(param, params[param])
        user = DbConnector().execute_get(sql)
        if user:
            return user[0]
        else:
            return None

    @classmethod
    def update_by_nickname(cls, nickname, params):
        sql = """
            UPDATE "user" SET
        """

        for i, key in enumerate(params):
            sql += """"{0}" = '{1}'""".format(key, params[key])
            if i < len(params) - 1:
                sql += """, """
        sql += " WHERE nickname='{0}'".format(SqlGenerator.safe_variable(nickname))
        sql += " RETURNING *;"
        user = DbConnector().execute_set_and_get(sql)[0]
        user.pop('id')
        return user
