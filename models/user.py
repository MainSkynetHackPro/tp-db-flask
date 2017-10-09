from models.model import Model


class User(Model):
    fields = (
        'id',
        'nickname',
        'fullname',
        'email',
        'about'
    )

    def __init__(self):
        super().__init__()
