from flask import Blueprint, Response

from models.forum import Forum
from models.post import Post
from models.thread import Thread
from models.user import User
from modules.dbconector import DbConnector
from modules.utils import json_response

service = Blueprint('service', __name__)


@service.route('/clear', methods=['POST'])
def clear_db():
    sql_table = """
        TRUNCATE TABLE "{0}";
    """
    sql = ""
    for item in (User, Forum, Post, Thread):
        sql += sql_table.format(item.tbl_name)

    DbConnector().execute_set(sql)
    return json_response({'status': 'ok'}, 200)


@service.route('/status', methods=['GET'])
def get_db_status():
    data = {
        'forum': Forum.get_count(),
        'post': Post.get_count(),
        'thread': Thread.get_count(),
        'user': User.get_count(),
    }
    return json_response(data, 200)
