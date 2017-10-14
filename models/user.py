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
