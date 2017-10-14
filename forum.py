from flask import Flask

from views.forum import view as forum
from views.service import service
from views.thread import thread
from views.user import view as user
from views.post import view as post

app = Flask(__name__)

app.register_blueprint(service, url_prefix='/service')

app.register_blueprint(forum, url_prefix='/forum')
app.register_blueprint(thread, url_prefix='/thread')
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(post, url_prefix='/post')
