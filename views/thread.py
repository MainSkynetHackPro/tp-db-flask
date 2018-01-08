from flask import Blueprint, request

from models.post import Post
from models.thread import Thread
from models.user import User
from models.vote import Vote
from modules.utils import json_response, format_time

thread = Blueprint('thread', __name__)


@thread.route('/<slug_or_id>/create', methods=['POST'])
def create_thread(slug_or_id):
    posts_data = request.get_json()
    thread = Thread.get_by_slug_or_id(slug_or_id)
    usernames = [i['author'] for i in posts_data]
    authors = User.get_user_ids_by_slug(usernames)
    if len(authors) != len(set(usernames)):
        return json_response(
            {'message': 'user not found'},
            404
        )
    for post in posts_data:
        for a in authors:
            if a['nickname'] == post['author'].lower():
                post['author_id'] = a['id']
        post['parent_id'] = post['parent'] if 'parent' in post else 0

    if len(thread) > 0:
        posts = Post.create_posts(posts_data, thread['id'])
    else:
        return json_response(
            {'message': 'thread not found'},
            404
        )
    for item in posts:
        item['created'] = format_time(item['created'])
    return json_response(
        posts,
        201
    )


@thread.route('/<slug_or_id>/details', methods=['GET'])
def get_thread_details(slug_or_id):
    thread = Thread.get_by_slug_or_id(slug_or_id)
    if thread:
        thread['created'] = format_time(thread['created'])
        return json_response(thread, 200)
    return json_response({'message': 'thread not found'}, 404)


@thread.route('/<slug_or_id>/details', methods=['POST'])
def update_thread(slug_or_id):
    return str(1)


@thread.route('/<slug_or_id>/posts', methods=['GET'])
def get_thread_messages(slug_or_id):
    return str(1)


@thread.route('/<slug_or_id>/vote', methods=['POST'])
def vote_thread(slug_or_id):
    post_data = request.get_json()
    thread = Thread.get_by_slug_or_id(slug_or_id)
    if not thread:
        return json_response({'message': 'Thread not found'}, 404)
    user = User().get_by_nickname(post_data['nickname'], hide_id=False)
    thread = Vote.vote_for_thread(user['id'], post_data['voice'], thread['id'])
    thread['created'] = format_time(thread['created'])
    return json_response(thread, 200)
