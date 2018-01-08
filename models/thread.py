from datetime import datetime

from models.dbmodel import DbModel
from models.forum import Forum
from models.model import Model
from models.user import User
from modules.dbconector import DbConnector
from modules.dbfield import DbField
from modules.sqlgenerator import SqlGenerator


class Thread(DbModel):
    tbl_name = 'thread'

    def __init__(self):
        super().__init__()

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
        data_tuple = tuple()
        sql = """
        SET TIME ZONE 'GMT+3';
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
        """.format(cls.tbl_name, User.tbl_name, Forum.tbl_name)
        sql += """
            WHERE LOWER(f.slug) = LOWER(%s)
        """
        data_tuple += (slug,)
        if since:
            if desc == 'true':
                sql += """
                    AND t.created <= %s
                """
            else:
                sql += """
                    AND t.created >= %s
                """
            data_tuple += (since,)
        if desc == 'true':
            sql += 'ORDER BY t.created DESC'
        else:
            sql += 'ORDER BY t.created'
        if limit:
            sql += " LIMIT {0}".format(int(limit))
        return DbConnector().execute_get(sql, data_tuple)

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

    @classmethod
    def get_by_slug_or_id(cls, slug_or_id):
        sql = """
        SELECT
          u.nickname as author,
          t.created,
          f.slug as forum,
          t.id,
          t.message,
          t.slug as slug,
          t.title,
          t.votes as votes
        FROM "{0}" as t
        JOIN "{1}" as u ON u.id = t.user_id
        JOIN "{2}" as f ON t.forum_id = f.id
        WHERE LOWER(t.slug) = LOWER(%s)
        """.format(cls.tbl_name, User.tbl_name, Forum.tbl_name)
        try:
            int(slug_or_id)
            sql += "or t.id = %s"
            data = (slug_or_id, slug_or_id,)
        except ValueError:
            data = (slug_or_id,)
        thread = DbConnector().execute_get(sql, data)
        return thread[0] if thread else []
