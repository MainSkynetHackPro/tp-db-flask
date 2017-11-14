from datetime import datetime

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
    def get_serialised_with_forum_user_by_id_or_slug(cls, id=None, slug=None):
        if slug:
            where_condition = """LOWER(t.slug)=LOWER('{0}')""".format(SqlGenerator.safe_variable(slug))
        else:
            where_condition = """t.id={0}""".format(id)

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
                WHERE {3}
            """.format(
            cls.tbl_name,
            User.tbl_name,
            Forum.tbl_name,
            where_condition
        )
        connector = DbConnector()
        data = connector.execute_get(sql)
        if data:
            return data[0]
        else:
            return None

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

    @classmethod
    def get_threads_list(cls, slug, limit, since, desc):
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
            WHERE t.created >= '{3}' AND LOWER(f.slug)=LOWER('{4}')
        """.format(cls.tbl_name, User.tbl_name, Forum.tbl_name, SqlGenerator.safe_variable(since), SqlGenerator.safe_variable(slug))
        if desc:
            sql += 'ORDER BY t.created DESC'
        else:
            sql += 'ORDER BY t.created'
        sql += " LIMIT {0}".format(limit)
        connector = DbConnector()
        return connector.execute_get(sql)

    @classmethod
    def create_and_get_serialized(cls, user_id, forum_id, title, message, created=None, slug=None):
        sql = """
            INSERT INTO {0}
            (user_id, forum_id, title, message, created{1})
            VALUES ({2}, {3}, '{4}', '{5}', {6}{7})
            RETURNING id, title, message, created{8}
        """.format(
            cls.tbl_name,
            ', slug' if slug else '',
            user_id,
            forum_id,
            title,
            message,
            "'{0}'".format(created if created else datetime.now()),
            """, '{0}'""".format(SqlGenerator.safe_variable(slug)) if slug else '',
            ', slug' if slug else ''
        )
        connector = DbConnector()
        return connector.execute_set_and_get(sql)[0]
