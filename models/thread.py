from models.forum import Forum
from models.model import Model
from models.user import User
from modules.dbconector import DbConnector
from modules.dbfield import DbField
from modules.sqlgenerator import SqlGenerator


class Thread(Model):
    tbl_name = 'thread'

    def __init__(self):
        self.id = DbField(name='id', type='SERIAL', primary_key=True)
        self.title = DbField(name='title', type='VARCHAR(50)', primary_key=False)
        self.message = DbField(name='message', type='TEXT', primary_key=False)
        self.slug = DbField(name='slug', type='VARCHAR(50)', primary_key=False)
        self.user_id = DbField(name='user_id', type='INT', primary_key=False)
        self.forum_id = DbField(name='forum_id', type='INT', primary_key=False)
        self.created = DbField(name='created', type='timestamp', primary_key=False)
        super().__init__()

    def create(self):
        """
        saves model to db
        """
        query = SqlGenerator(self.tbl_name, SqlGenerator.TYPE_INSERT)
        query.values(self._serialize())
        sql = query.get_sql()
        sql += """
            UPDATE "{0}"
            SET count_threads = count_threads + 1
            WHERE id='{1}';
        """.format(Forum.tbl_name, self.forum_id)
        connector = DbConnector()
        connector.execute_set(sql)
        self.exists = True

    @classmethod
    def get_serialised_with_forum_user_by_title(cls, slug):
        sql = """
            SELECT
              u.nickname as author,
              t.created,
              f.slug as forum,
              t.id,
              t.message,
              t.slug as slug,
              t.title,
              0 as votes
            FROM "{0}" as t
            JOIN "{1}" as u ON u.id = t.user_id
            JOIN "{2}" as f ON t.forum_id = f.id
            WHERE t.slug='{3}'
        """.format(cls.tbl_name, User.tbl_name, Forum.tbl_name, SqlGenerator.safe_variable(slug))
        connector = DbConnector()
        data = connector.execute_get(sql)
        if data:
            return data[0]
        else:
            return None
