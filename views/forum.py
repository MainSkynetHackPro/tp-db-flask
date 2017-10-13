from flask import Blueprint, json, request
from models.forum import Forum
from models.thread import Thread
from models.user import User

view = Blueprint('forum', __name__)


@view.route('/create', methods=['POST'])
def create_forum():
    json_data = request.get_json()
    user = User().get({'nickname': json_data['user']})
    if not user.exists:
        return json.dumps({
            "message": "Can't find user with nickname {0}".format(json_data['user'])
        }), 404
    forum_exists = Forum.get_serialised_with_user(json_data['slug'])
    if forum_exists:
        return json.dumps(forum_exists), 409
    forum = Forum()
    forum.load_from_dict(json_data)
    forum.user_id.val(user.id)
    forum.save()
    return json.dumps(forum.serialize(use_alias=True)), 201


@view.route('/<slug>/create', methods=['POST'])
def create_branch(slug):
    json_data = request.get_json()
    user = User().get({'nickname': json_data['author']})
    forum = Forum().get({'slug': slug})
    if not (user.exists and forum.exists):
        return json.dumps({
            "message": "Can't find user or forum"
        }), 404
    thread_exists = Thread.get_serialised_with_forum_user_by_title(json_data['slug'])
    if thread_exists:
        return json.dumps(thread_exists), 409
    thread = Thread()
    thread.load_from_dict(json_data)
    thread.forum_id.val(forum.id)
    thread.user_id.val(user.id)
    thread.save()
    return json.dumps(Thread.get_serialised_with_forum_user_by_title(json_data['slug']))


@view.route('/<slug>/details', methods=['GET'])
def get_forum_details(slug):
    serialised_forum = Forum.get_serialised_with_user(slug)
    return json.dumps(serialised_forum)


@view.route('/<slug>/threads', methods=['GET'])
def get_threads_list(slug):
    limit = request.args.get('limit')
    since = request.args.get('since')
    desc = request.args.get('desc')
    thread = Thread().get({'slug': slug})
    if not thread.exists:
        return json.dumps({
            "message": "Can't find forum"
        }), 404
    threads = Thread.get_threads_list(slug, limit, since, desc)
    return json.dumps(threads)


@view.route('/<slug>/users', methods=['GET'])
def get_forum_users(slug):
    limit = request.args.get('limit')
    since = request.args.get('since')
    desc = request.args.get('desc')
    thread = Thread().get({'slug': slug})
    if not thread.exists:
        return json.dumps({
            "message": "Can't find forum"
        }), 404
    users = Forum.get_forum_users(slug, limit, since, desc)
    return json.dumps(users)

#
# @view.route('/<id>/details', methods=['GET'])
# def get_post_details(id):
#     return id
#
#
# @view.route('/<id>/details', methods=['POST'])
# def change_post_message(id):
#     return id
#


