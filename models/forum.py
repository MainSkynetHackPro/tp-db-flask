from models.model import Model
from modules.dbfield import DbField


class Forum(Model):
    tbl_name = 'forum'

    def __init__(self):
        self.id = DbField(name='id', type='SERIAL', primary_key=True)
        self.slug = DbField(name='slug', type='VARCHAR(50)', primary_key=False)
        self.user_id = DbField(name='user_id', type='INT', primary_key=False)
        self.count_threads = DbField(name='count_threads', type='INT', primary_key=False)
        self.count_posts = DbField(name='count_posts', type='INT', primary_key=False)
        super().__init__()
