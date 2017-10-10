from models.model import Model
from modules.dbfield import DbField


class User(Model):
    tbl_name = 'user'

    def __init__(self):
        self.pk = DbField(name='pk', type='SERIAL', primary_key=True)
        self.nickname = DbField(name='nickname', type='VARCHAR(25)', primary_key=False)
        self.fullname = DbField(name='fullname', type='VARCHAR(25)', primary_key=False)
        self.email = DbField(name='email', type='VARCHAR(25)', primary_key=False)
        self.about = DbField(name='about', type='VARCHAR(128)', primary_key=False)
        super().__init__()
