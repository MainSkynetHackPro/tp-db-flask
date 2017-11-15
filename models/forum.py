from models.dbmodel import DbModel
from models.user import User
from modules.dbconector import DbConnector


class Forum(DbModel):
    tbl_name = 'tbl_forum'

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
        return DbConnector().execute_set_and_get(sql)[0]

    def get_by_slug(self, slug):
        sql = """
            SELECT 
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
        data = DbConnector().execute_get(sql)
        return data[0] if data else []


