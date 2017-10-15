from models.model import Model
from models.user import User
from modules.dbconector import DbConnector
from modules.dbfield import DbField
from modules.sqlgenerator import SqlGenerator


class Forum(Model):
    tbl_name = 'forum'

    def __init__(self):
        self.id = DbField(name='id', type='SERIAL', primary_key=True)
        self.slug = DbField(name='slug', type='VARCHAR(50)', primary_key=False)
        self.title = DbField(name='title', type='VARCHAR(50)', primary_key=False)
        self.user_id = DbField(name='user_id', type='INT', primary_key=False)
        self.count_threads = DbField(name='count_threads', type='INT', primary_key=False, default=0, alias='threads')
        self.count_posts = DbField(name='count_posts', type='INT', primary_key=False, default=0, alias='posts')
        super().__init__()

    @classmethod
    def get_serialised_with_user(cls, slug):
        sql = """
            SELECT 
                f.title,
                f.slug,
                f.count_threads as threads,
                f.count_posts as posts,
                u.nickname as user
            FROM "{0}" as f
              JOIN "{1}" as u ON f.user_id = u.id
            WHERE LOWER(f.slug) = LOWER('{2}')
        """.format(
            cls.tbl_name,
            User.tbl_name,
            SqlGenerator.safe_variable(slug)
        )
        connector = DbConnector()
        data = connector.execute_get(sql)
        if data:
            return data[0]
        else:
            return None

    @classmethod
    def get_forum_users(cls, slug, limit, since, desc):
        pass

    @classmethod
    def create_and_get_serialized(cls, user_id, title, slug):
        sql = """
            INSERT INTO forum (user_id, title, slug)
            VALUES ({0}, '{1}', '{2}')
            RETURNING forum.slug, forum.title
        """.format(
            SqlGenerator.safe_variable(user_id),
            SqlGenerator.safe_variable(title),
            SqlGenerator.safe_variable(slug)
        )
        return DbConnector().execute_set_and_get(sql)[0]
