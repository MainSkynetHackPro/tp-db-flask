from models.model import Model
from modules.dbfield import DbField


class User(Model):
    tbl_name = 'user'
    pk = DbField(name='pk', type='SERIAL', primary_key=True)
    nickname = DbField(name='nickname', type='CHAR(25)', primary_key=False)
    fullname = DbField(name='fullname', type='CHAR(25)', primary_key=False)
    email = DbField(name='email', type='CHAR(25)', primary_key=False)
    about = DbField(name='about', type='CHAR(128)', primary_key=False)

    def __init__(self):
        super().__init__()
