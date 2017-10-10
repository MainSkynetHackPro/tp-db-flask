from models.model import Model
from modules.dbfield import DbField


class User(Model):
    tbl_name = 'user'
    pk = DbField(name='pk', type='SERIAL', primary_key=True)
    nickname = DbField(name='nickname', type='VARCHAR(25)', primary_key=False)
    fullname = DbField(name='fullname', type='VARCHAR(25)', primary_key=False)
    email = DbField(name='email', type='VARCHAR(25)', primary_key=False)
    about = DbField(name='about', type='VARCHAR(128)', primary_key=False)

    def __init__(self):
        super().__init__()
