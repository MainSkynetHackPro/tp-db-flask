from models.forum import Forum
from models.model import Model
from models.thread import Thread
from models.user import User
from modules.dbconector import DbConnector


class Post(Model):
    tbl_name = 'posts'
    @classmethod
    def create_posts(cls, posts_data, thread_id):
        insert_data = tuple()
        if not posts_data:
            return []
        sql = """
            INSERT INTO {tbl_name} (user_id, thread_id, parent_id, message) VALUES
        """.format_map({'tbl_name': cls.tbl_name})
        for post in posts_data:
            sql += "(%s, %s, %s, %s),"
            insert_data += (
                post['author_id'],
                thread_id,
                post['parent_id'],
                post['message']
            )
        sql = sql[:-1]
        sql += """
            RETURNING id
        """
        ids = DbConnector().execute_set_and_get(sql, insert_data)
        sql = """
            SELECT
              m.nickname as author,
              p.created as created,
              f.slug as forum,
              p.id as id,
              p.message as message,
              p.thread_id as thread,
              p.parent_id as parent
            FROM {tbl_name} AS p
            JOIN {u_tbl_name} AS m ON m.id = p.user_id
            JOIN {t_tbl_name} AS t ON t.id = p.thread_id
            JOIN {f_tbl_name} AS f ON f.id = t.forum_id
            WHERE p.id in (
        """.format_map({
            'tbl_name': cls.tbl_name,
            'u_tbl_name': User.tbl_name,
            't_tbl_name': Thread.tbl_name,
            'f_tbl_name': Forum.tbl_name,
        })

        for i in ids:
            sql += "{0}, ".format(i['id'])
        sql = sql[:-2] + ")"
        return DbConnector().execute_get(sql)

