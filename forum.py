from flask import Flask

from views.forum import view as forum
from views.service import service
from views.thread import thread
from views.user import view as user

app = Flask(__name__)

app.register_blueprint(service, url_prefix='/api/service')

app.register_blueprint(forum, url_prefix='/api/forum')
app.register_blueprint(thread, url_prefix='/api/thread')
app.register_blueprint(user, url_prefix='/api/user')
