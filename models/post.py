from models.dbmodel import DbModel
from models.forum import Forum
from models.thread import Thread
from models.user import User
from modules.dbconector import DbConnector
from modules.utils import format_time


class Post(DbModel):
    tbl_name = 'posts'

    @classmethod
    def create_posts(cls, posts_data, thread_id, forum_id):
        insert_data = tuple()
        if not posts_data:
            return []
        rel_insert = ""
        for post in posts_data:
            rel_insert += "(%s, %s, %s), "
            insert_data += (
                post['author_id'],
                forum_id,
                post['author_nickname']
            )
        rel_insert = rel_insert[:-2]
        sql = """
            UPDATE forum SET count_posts = count_posts + {count_posts} WHERE id = {forum_id};
            INSERT INTO user_forum 
            (user_id, forum_id, user_nickname) VALUES
            {rel_insert} ON CONFLICT DO NOTHING;
            INSERT INTO {tbl_name} (user_id, thread_id, parent_id, message) VALUES
        """.format_map({
            'tbl_name': cls.tbl_name,
            'count_posts': len(posts_data),
            'forum_id': forum_id,
            'rel_insert': rel_insert
        })
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
        ids = DbConnector.execute_set_and_get(sql, insert_data)
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
        sql = sql[:-2] + ")" + " ORDER BY id"
        return DbConnector.execute_get(sql)

    @classmethod
    def get_info(cls, post_id, related):
        sql = """
            SELECT
              m.nickname as author,
              p.created as created,
              f.slug as forum,
              p.id as id,
              p.message as message,
              p.thread_id as thread,
              p.parent_id as parent,
              p.is_edited as isEdited
            FROM {tbl_name} AS p
            JOIN {u_tbl_name} AS m ON m.id = p.user_id
            JOIN {t_tbl_name} AS t ON t.id = p.thread_id
            JOIN {f_tbl_name} AS f ON f.id = t.forum_id
            WHERE p.id = %(post_id)s
            """.format_map({
                'tbl_name': cls.tbl_name,
                'u_tbl_name': User.tbl_name,
                't_tbl_name': Thread.tbl_name,
                'f_tbl_name': Forum.tbl_name,
            })

        post = DbConnector.execute_get(sql, {'post_id': post_id})
        if post:
            post[0]['isEdited'] = post[0]['isedited']
            post[0]['created'] = format_time(post[0]['created'])
        data = {'post': post[0] if post else None}
        if related and post:
            related = related.split(',')
            if 'user' in related:
                data['author'] = User().get_by_nickname(post[0]['author'])
            if 'thread' in related:
                data['thread'] = Thread.get_serialised_with_forum_user_by_id_or_slug(id=post[0]['thread'])
                data['thread']['created'] = format_time(data['thread']['created'])
            if 'forum' in related:
                data['forum'] = Forum().get_by_slug(post[0]['forum'])
        return data

    @classmethod
    def get_post(cls, post_id):
        sql = """
                    SELECT
                      m.nickname as author,
                      p.created as created,
                      f.slug as forum,
                      p.id as id,
                      p.message as message,
                      p.thread_id as thread,
                      p.parent_id as parent,
                      p.is_edited as isEdited
                    FROM {tbl_name} AS p
                    JOIN {u_tbl_name} AS m ON m.id = p.user_id
                    JOIN {t_tbl_name} AS t ON t.id = p.thread_id
                    JOIN {f_tbl_name} AS f ON f.id = t.forum_id
                    WHERE p.id = %(post_id)s
                    """.format_map({
            'tbl_name': cls.tbl_name,
            'u_tbl_name': User.tbl_name,
            't_tbl_name': Thread.tbl_name,
            'f_tbl_name': Forum.tbl_name,
        })

        post = DbConnector.execute_get(sql, {'post_id': post_id})
        if post:
            post[0]['created'] = format_time(post[0]['created'])
        return post[0] if post else []

    @classmethod
    def update_post(cls, post_id, update_data, old_post):
        if not update_data:
            return old_post
        update = False
        for key, value in update_data.items():
            if value != old_post[key]:
                update = True
        if not update:
            return old_post
        update_statement = ''
        data = tuple()
        for key, item in update_data.items():
            old_post[key] = item
            update_statement += '{0} = %s, '.format(key)
            data += item,
        update_statement += "is_edited = true"
        old_post['isEdited'] = True
        sql = """
                    UPDATE {tbl_name} SET {update_statement} WHERE id = {post_id}
                """.format_map({
            'tbl_name': cls.tbl_name,
            'update_statement': update_statement,
            'post_id': post_id,
        })
        DbConnector.execute_set(sql, data)
        return old_post

    @classmethod
    def get_posts_by_id_in_thread(cls, thread_id, posts_ids):
        in_condition = ''
        in_vars = tuple()
        for id in posts_ids:
            in_condition += " %s,"
            in_vars += (id, )
        in_condition = in_condition[:-1]
        sql = """
            SELECT
                p.id
            FROM {tbl_posts} AS p
            WHERE p.id in ({in_condition}) AND p.thread_id = {thread_id}
        """.format_map({
            'tbl_posts': Post.tbl_name,
            'in_condition': in_condition,
            'thread_id': thread_id
        })
        return DbConnector.execute_get(sql, in_vars)

