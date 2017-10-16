from flask import Blueprint, json, request, Response
from models.forum import Forum
from models.thread import Thread
from models.user import User

view = Blueprint('forum', __name__)


@view.route('/create', methods=['POST'])
def create_forum():
    json_data = request.get_json()
    user = User.get_user_by_nickname(json_data['user'], hide_id=False)
    if not user:
        return Response(
            response=json.dumps({
                "message": "Can't find user with nickname {0}".format(json_data['user'])
            }),
            status=404,
            mimetype="application/json"
        )
    if 'slug' in json_data.keys():
        forum_exists = Forum.get_serialised_with_user(slug=json_data['slug'])
        if forum_exists:
            return Response(
                response=json.dumps(forum_exists),
                status=409,
                mimetype="application/json"
            )
    forum = Forum.create_and_get_serialized(user_id=user['id'], title=json_data['title'],
                                            slug=json_data['slug'] if 'slug' in json_data.keys() else None)
    forum['user'] = user['nickname']
    forum.pop('user_id', None)
    return Response(
        response=json.dumps(forum),
        status=201,
        mimetype="application/json"
    )


@view.route('/<slug>/create', methods=['POST'])
def create_thread(slug):
    json_data = request.get_json()
    user = User.get_user_by_nickname(json_data['author'], hide_id=False)
    forum = Forum.get_serialised_with_user(slug, hide_id=False)
    if not (user and forum):
        return json.dumps({
            "message": "Can't find user or forum"
        }), 404
    if 'slug' in json_data.keys():
        thread_exists = Thread.get_serialised_with_forum_user_by_id_or_slug(slug=json_data['slug'])
        if thread_exists:
            return json.dumps(thread_exists), 409
    thread = Thread.create_and_get_serialized(
        user_id=user['id'],
        forum_id=forum['id'],
        title=json_data['title'],
        message=json_data['message'],
        created=json_data['created'],
    )
    thread['author'] = user['nickname']
    thread['forum'] = forum['slug']
    thread['created'] = thread['created'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return Response(
        response=json.dumps(thread),
        status=201,
        mimetype="application/json"
    )


@view.route('/<slug>/details', methods=['GET'])
def get_forum_details(slug):
    forum = Forum.get_serialised_with_user(slug)
    if not forum:
        return Response(
            response=json.dumps({
                "message": "Can't find forum with slug: {0}".format(slug)
            }),
            status=404,
            mimetype="application/json"
        )
    return Response(
        response=json.dumps(forum),
        status=200,
        mimetype="application/json"
    )


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
