from flask import Blueprint, json, request
from models.forum import Forum
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
    return slug


@view.route('/<slug>/details', methods=['GET'])
def get_forum_details(slug):
    serialised_forum = Forum.get_serialised_with_user(slug)
    return json.dumps(serialised_forum)


@view.route('/<slug>/threads', methods=['GET'])
def get_threads_list(slug):
    return slug


@view.route('/<slug>/users', methods=['GET'])
def get_forum_users(slug):
    return slug

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


