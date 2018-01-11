from models.dbmodel import DbModel
from models.user import User
from modules.dbconector import DbConnector


class Forum(DbModel):
    tbl_name = 'forum'

    def sql_select(self, hide_id=True):
        additional = ''
        if not hide_id:
            additional = """
                {tbl_name}.id,
                {tbl_user}.id as user_id,
            """.format(**{
                'tbl_name': self.tbl_name,
                'tbl_user': User.tbl_name
            })
        return """
            SELECT 
              {additional}
              {tbl_user}.nickname as user,
              {tbl_name}.slug,
              {tbl_name}.tilte
            FROM {tbl_name}        
            JOIN {tbl_user} ON {tbl_user}.id = {tbl_name}.user_id
        """.format(**{
            'tbl_name': self.tbl_name,
            'tbl_user': User.tbl_name,
            'additional': additional
        })

    def create(self, payload):
        sql = """
            WITH f AS (
              INSERT INTO {tbl_name}
              (user_id, slug, title)
              VALUES ({user_id}, '{slug}', '{title}')
              RETURNING user_id, slug, title)
            SELECT 
              {tbl_user}.nickname as user,
              f.slug,
              f.title
            FROM f
            JOIN {tbl_user} ON {tbl_user}.id = f.user_id
        """.format(**{
            'tbl_name': self.tbl_name,
            'tbl_user': User.tbl_name,
            'user_id': payload['user_id'],
            'slug': payload['slug'],
            'title': payload['title']
        })
        return DbConnector.execute_set_and_get(sql)[0]

    def get_by_slug(self, slug):
        sql = """
            SELECT 
              {tbl_user}.nickname as user,
              {tbl_name}.slug,
              {tbl_name}.title,
              {tbl_name}.count_posts AS posts,
              {tbl_name}.count_threads AS threads
            FROM {tbl_name}        
            JOIN {tbl_user} ON {tbl_user}.id = {tbl_name}.user_id
            WHERE LOWER({tbl_name}.slug) = LOWER('{slug}')
        """.format(**{
            'sql_select': self.sql_select(),
            'tbl_name': self.tbl_name,
            'tbl_user': User.tbl_name,
            'slug': slug
        })
        data = DbConnector.execute_get(sql)
        return data[0] if data else []

    def get_by_slug_with_id(self, slug):
        sql = """
            SELECT 
              {tbl_name}.id,
              {tbl_user}.nickname as user,
              {tbl_name}.slug,
              {tbl_name}.title
            FROM {tbl_name}        
            JOIN {tbl_user} ON {tbl_user}.id = {tbl_name}.user_id
            WHERE LOWER({tbl_name}.slug) = LOWER('{slug}')
        """.format(**{
            'sql_select': self.sql_select(),
            'tbl_name': self.tbl_name,
            'tbl_user': User.tbl_name,
            'slug': slug
        })
        data = DbConnector.execute_get(sql)
        return data[0] if data else []

    @classmethod
    def get_serialised_with_user(cls, slug):
        sql = """
            SELECT
              forum.count_posts as posts,
              forum.slug,
              forum.count_threads as threads,
              forum.title,
              member.nickname as user
            FROM forum
            JOIN member ON member.id = forum.user_id
            WHERE LOWER(forum.slug) = LOWER(%s)
        """
        data = DbConnector.execute_get(sql, (slug,))
        return data[0] if data else None

    @classmethod
    def get_forum_users(cls, forum_id, limit, since, desc):
        from models.post import Post
        from models.thread import Thread
        sql = """
            SELECT 
                u.nickname,
                u.about,
                u.email,
                u.fullname
            FROM {tbl_forum} AS f 
            INNER JOIN {tbl_thread} AS t ON t.forum_id = f.id
            INNER JOIN {tbl_post} AS p ON p.thread_id = t.id
            INNER JOIN {tbl_user} AS u ON u.id = p.user_id OR u.id = t.user_id
            WHERE f.id = {forum_id} {additional_where}
            GROUP BY u.id
            ORDER BY u.nickname {additional_order}
            {limit}
        """.format_map({
            'tbl_forum': cls.tbl_name,
            'tbl_thread': Thread.tbl_name,
            'tbl_post': Post.tbl_name,
            'tbl_user': User.tbl_name,
            'forum_id': forum_id,
            'additional_order': "DESC " if desc == 'true' else " ",
            'limit': "LIMIT %(limit)s " if limit else " ",
            'additional_where': "AND lower(u.nickname) > lower(%(since)s)" if since else " ",
        })

        data = {}
        if limit:
            data['limit'] = limit
        if since:
            data['since'] = since
        if desc == 'true':
            sql = sql.replace('>', '<')
        return DbConnector.execute_get(sql, data)
