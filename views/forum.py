from flask import Blueprint, json, request, Response
from models.forum import Forum
from models.thread import Thread
from models.user import User
from modules.utils import format_time, json_response

view = Blueprint('forum', __name__)


@view.route('/create', methods=['POST'])
def create_forum():
    json_data = request.get_json()
    user = User().get_by_nickname(json_data['user'], hide_id=False)
    if not user:
        return json_response(
            {
                "message": "Can't find user with nickname {0}".format(json_data['user'])
            },
            404
        )
    if 'slug' in json_data.keys():
        forum_exists = Forum().get_by_slug(slug=json_data['slug'])
        if forum_exists:
            return json_response(forum_exists, 409)
    json_data.pop('user')
    json_data['user_id'] = user['id']
    forum = Forum().create(payload=json_data)
    return json_response(
        forum,
        201,
    )


@view.route('/<slug>/create', methods=['POST'])
def create_thread(slug):
    json_data = request.get_json()
    user = User().get_by_nickname(json_data['author'], hide_id=False)
    forum = Forum().get_by_slug_with_id(slug)
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
        created=json_data['created'] if 'created' in json_data else None,
        slug=json_data['slug'] if 'slug' in json_data else None
    )
    thread['author'] = user['nickname']
    thread['forum'] = forum['slug']
    thread['created'] = format_time(thread['created'])
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
    if not since:
        since = "0001-01-01T00:00:00.000Z"
    threads = Thread.get_threads_list(slug, limit, since, desc)
    if threads:
        return Response(
                response=json.dumps(threads),
                status=200,
                mimetype="application/json"
            )
    else:
        return json_response(
            {'message': 'not found'},
            404
        )


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

