from models.model import Model


class Post(Model):
    tbl_name = 'posts'
    @classmethod
    def create_posts(cls, posts_data):
        sql = """
            INSERT INTO {tbl_name} ()
        """.format_map({'tbl_name': cls.tbl_name})
