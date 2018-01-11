from datetime import datetime

from models.dbmodel import DbModel
from models.forum import Forum
from models.user import User
from modules.dbconector import DbConnector


class Thread(DbModel):
    tbl_name = 'thread'

    def __init__(self):
        super().__init__()

    @classmethod
    def get_serialised_with_forum_user_by_id_or_slug(cls, id=None, slug=None):
        if slug:
            where_condition = """LOWER(t.slug)=LOWER('{0}')""".format(slug)
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
                  t.votes as votes
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
        connector = DbConnector
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
        """.format(cls.tbl_name, User.tbl_name, Forum.tbl_name, slug)
        connector = DbConnector
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
              t.votes as votes
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
        return DbConnector.execute_get(sql, data_tuple)

    @classmethod
    def create_and_get_serialized(cls, user_id, forum_id, title, message, created=None, slug=None):
        sql = """
            UPDATE forum SET count_threads = count_threads + 1 WHERE id = {3};
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
            """, '{0}'""".format(slug) if slug else '',
            ', slug' if slug else ''
        )
        connector = DbConnector
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
        thread = DbConnector.execute_get(sql, data)
        return thread[0] if thread else []

    @classmethod
    def get_by_slug_or_id_with_forum_id(cls, slug_or_id):
        sql = """
                SELECT
                  u.nickname as author,
                  t.created,
                  f.slug as forum,
                  t.id,
                  t.message,
                  t.slug as slug,
                  t.title,
                  t.votes as votes,
                  f.id as forum_id
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
        thread = DbConnector.execute_get(sql, data)
        return thread[0] if thread else []

    @classmethod
    def get_posts_flat_sorted(cls, thread_id, since, limit, desc):
        from models.post import Post

        sql = """
            SELECT
                p.id AS id,
                p.created AS created,
                p.is_edited AS isEdited,
                p.message AS message,
                p.parent_id AS parent,
                p.thread_id AS thread,
                u.nickname AS author,
                f.slug AS forum
            FROM {tbl_post} AS p
            JOIN {tbl_user} AS u ON u.id = p.user_id
            JOIN {tbl_thread} AS t ON t.id = p.thread_id
            JOIN {tbl_forum} AS f ON f.id = t.forum_id
            WHERE t.id = %(thread_id)s {where_additional}
            ORDER BY p.created {order_direction}, p.id {order_direction}
            {limit_statement}
        """.format_map({
            'tbl_post': Post.tbl_name,
            'tbl_user': User.tbl_name,
            'tbl_thread': Thread.tbl_name,
            'tbl_forum': Forum.tbl_name,
            'where_additional': "AND p.id > %(since_id)s" if since else " ",
            'order_direction': "DESC " if desc == "true" else "ASC ",
            'limit_statement': "LIMIT %(limit)s" if limit else " "
        })
        if desc == "true":
            sql = sql.replace('>', '<')
        data = {
            'thread_id': thread_id,
        }
        if limit:
            data['limit'] = limit
        if since:
            data['since_id'] = since
        return DbConnector.execute_get(sql, data)

    @classmethod
    def get_posts_tree_sorted(cls, thread_id, since, limit, desc):
        from models.post import Post

        sql = """
            SELECT
                p.id AS id,
                p.created AS created,
                p.is_edited AS isEdited,
                p.message AS message,
                p.parent_id AS parent,
                p.thread_id AS thread,
                u.nickname AS author,
                f.slug AS forum
            FROM {tbl_post} AS p
            JOIN {tbl_user} AS u ON u.id = p.user_id
            JOIN {tbl_thread} AS t ON t.id = p.thread_id
            JOIN {tbl_forum} AS f ON f.id = t.forum_id
            WHERE t.id = %(thread_id)s {where_additional}
            ORDER BY p.path {order_direction}
            {limit_statement}
        """.format_map({
            'tbl_post': Post.tbl_name,
            'tbl_user': User.tbl_name,
            'tbl_thread': Thread.tbl_name,
            'tbl_forum': Forum.tbl_name,
            'where_additional': "AND p.path > (SELECT path FROM Posts WHERE id = %(since)s) " if since else " ",
            'order_direction': "DESC " if desc == "true" else "ASC ",
            'limit_statement': "LIMIT %(limit)s" if limit else " "
        })
        data = {
            'thread_id': thread_id,
        }
        if limit:
            data['limit'] = limit
        if since:
            data['since'] = since
        if desc == "true":
            sql = sql.replace('>', '<')
        return DbConnector.execute_get(sql, data)

    @classmethod
    def get_posts_parent_tree_sorter(cls, thread_id, since, limit, desc):
        from models.post import Post
        if since:
            sql = """
            WITH RECURSIVE temp(
                id,
                created,
                isEdited,
                message,
                parent,
                thread,
                author,
                forum,
                PATH,
                LEVEL
            ) AS (
                SELECT
                    p.id AS id,
                    p.created AS created,
                    p.is_edited AS isEdited,
                    p.message AS message,
                    p.parent_id AS parent,
                    p.thread_id AS thread,
                    u.nickname AS author,
                    f.slug AS forum,
                    array[p.id] as PATH,
                    1
                FROM (
                  SELECT id, user_id, created, is_edited, message, parent_id, thread_id FROM {tbl_post}
                  WHERE parent_id = 0 AND thread_id = %(thread_id)s
                ) AS p
                JOIN {tbl_user} AS u ON u.id = p.user_id
                JOIN {tbl_thread} AS t ON t.id = p.thread_id
                JOIN {tbl_forum} AS f ON f.id = t.forum_id
                WHERE p.parent_id = 0 AND p.thread_id = %(thread_id)s
                UNION SELECT 
                  p.id,
                  p.created,
                  p.is_edited as isEdited,
                  p.message,
                  p.parent_id as parent,
                  p.thread_id as thread,
                  u.nickname as nickname,
                  f.slug as forum,
                  temp.PATH || p.id, LEVEL + 1
                FROM {tbl_post} AS p
                JOIN {tbl_user} AS u ON u.id = p.user_id
                JOIN {tbl_thread} AS t ON t.id = p.thread_id
                JOIN {tbl_forum} AS f ON f.id = t.forum_id
                JOIN temp ON temp.id = p.parent_id
                WHERE p.thread_id = %(thread_id)s
            ), rows AS(
                SELECT row_number() OVER (ORDER BY PATH) AS row_num, id, author, created, forum, isEdited, 
                message, parent, thread, PATH, LEVEL FROM temp
            ), one_row AS (
                SELECT * FROM rows where id = %(since)s
            )
            SELECT 
              rows.id,
              rows.author,
              rows.created,
              rows.forum,
              rows.isEdited,
              rows.message,
              rows.parent,
              rows.thread
            FROM rows, one_row
            WHERE rows.row_num > one_row.row_num
            ORDER BY rows.PATH {additional_order}
        """.format_map({
                'tbl_post': Post.tbl_name,
                'tbl_user': User.tbl_name,
                'tbl_thread': Thread.tbl_name,
                'tbl_forum': Forum.tbl_name,
                'additional_order': "DESC " if desc == "true" else "ASC ",
            })
        else:
            sql = """
                WITH RECURSIVE temp(
                    id,
                    created,
                    isEdited,
                    message,
                    parent,
                    thread,
                    author,
                    forum,
                    PATH,
                    LEVEL
                ) AS (
                    SELECT
                        p.id AS id,
                        p.created AS created,
                        p.is_edited AS isEdited,
                        p.message AS message,
                        p.parent_id AS parent,
                        p.thread_id AS thread,
                        u.nickname AS author,
                        f.slug AS forum,
                        array[p.id] as PATH,
                        1
                    FROM (
                      SELECT id, user_id, created, is_edited, message, parent_id, thread_id FROM {tbl_post}
                      WHERE parent_id = 0 AND thread_id = %(thread_id)s
                      ORDER BY id {additional_order}
                      {limit_statement}
                    ) AS p
                    JOIN {tbl_user} AS u ON u.id = p.user_id
                    JOIN {tbl_thread} AS t ON t.id = p.thread_id
                    JOIN {tbl_forum} AS f ON f.id = t.forum_id
                    WHERE p.parent_id = 0 AND p.thread_id = %(thread_id)s
                    UNION SELECT 
                        p.id AS id,
                        p.created AS created,
                        p.is_edited AS isEdited,
                        p.message AS message,
                        p.parent_id AS parent,
                        p.thread_id AS thread,
                        u.nickname AS author,
                        f.slug AS forum,
                        temp.PATH || p.id, LEVEL + 1
                    FROM {tbl_post} AS p
                    JOIN {tbl_user} AS u ON u.id = p.user_id
                    JOIN {tbl_thread} AS t ON t.id = p.thread_id
                    JOIN {tbl_forum} AS f ON f.id = t.forum_id
                    JOIN temp ON temp.id = p.parent_id
                    WHERE p.thread_id = %(thread_id)s
                )
                SELECT 
                  *
                FROM temp
                ORDER BY PATH {additional_order}
            """.format_map({
                'tbl_post': Post.tbl_name,
                'tbl_user': User.tbl_name,
                'tbl_thread': Thread.tbl_name,
                'tbl_forum': Forum.tbl_name,
                'additional_order': "DESC " if desc == "true" else "ASC ",
                'limit_statement': "LIMIT %(limit)s" if limit else ""
            })
        data = {
            'thread_id': thread_id,
        }
        if limit:
            data['limit'] = limit
        if since:
            data['since'] = since
        if desc == "true":
            sql = sql.replace('>', '<')
        return DbConnector.execute_get(sql, data)

    @classmethod
    def update_thread(cls, thread_id, update_data, bedore_update):
        if not update_data:
            return bedore_update
        update_statement = ''
        data = tuple()
        for key, item in update_data.items():
            bedore_update[key] = item
            update_statement += '{0} = %s, '.format(key)
            data += item,
        update_statement = update_statement[:-2]
        sql = """
            UPDATE {tbl_name} SET {update_statement} WHERE id = {thread_id}
        """.format_map({
            'tbl_name': cls.tbl_name,
            'update_statement': update_statement,
            'thread_id': thread_id,
        })
        DbConnector.execute_set(sql, data)
        return bedore_update

    @classmethod
    def check_user_and_thread(cls, thread_slug_or_id, nickname):
        if thread_slug_or_id.isdigit():
            thread_where_statement = "t.id = %(slug_or_id)s "
        else:
            thread_where_statement = "LOWER(t.slug) = %(slug_or_id)s "
            thread_slug_or_id = thread_slug_or_id.lower()
        sql = """
            SELECT
                'thread_id' AS sub,
                t.id AS id
            FROM {tbl_thread} AS t
            WHERE {thread_where_statement}
            UNION
            SELECT 
                'user_id' AS sub,
                u.id AS id
            FROM {tbl_user} AS u
            WHERE LOWER(u.nickname) = %(lowered_nickname)s
            ORDER BY sub
        """.format_map({
            'tbl_thread': cls.tbl_name,
            'tbl_user': User.tbl_name,
            'thread_where_statement': thread_where_statement
        })

        data = DbConnector.execute_get(sql, {
            'lowered_nickname': nickname.lower(),
            'slug_or_id': thread_slug_or_id
        })
        if len(data) == 2:
            return data[0]['id'], data[1]['id']
        else:
            return None, None

