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
    thread = Thread.get_by_slug_or_id_with_forum_id(slug_or_id)
    usernames = [i['author'] for i in posts_data]
    authors = User.get_user_ids_by_slug(usernames)
    posts_ids = set([i['parent'] for i in posts_data if 'parent' in i])
    if posts_ids:
        posts = Post.get_posts_by_id_in_thread(thread['id'], posts_ids)
        if len(posts) != len(posts_ids):
            return json_response({'message': 'Parent in other thread'}, 409)
    if len(authors) != len(set(usernames)):
        return json_response(
            {'message': 'user not found'},
            404
        )
    for post in posts_data:
        for a in authors:
            if a['nickname'] == post['author'].lower():
                post['author_id'] = a['id']
                post['author_nickname'] = a['nickname']
        post['parent_id'] = post['parent'] if 'parent' in post else 0

    if len(thread) > 0:
        posts = Post.create_posts(posts_data, thread['id'], thread['forum_id'])
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
    json_data = request.get_json()
    thread = Thread.get_by_slug_or_id(slug_or_id)
    if not thread:
        return json_response({'message': 'Thread not found'}, 404)
    thread = Thread.update_thread(thread['id'], json_data, thread)
    thread['created'] = format_time(thread['created'])
    return json_response(thread, 200)


@thread.route('/<slug_or_id>/posts', methods=['GET'])
def get_thread_messages(slug_or_id):
    sort = request.args.get('sort')
    since = request.args.get('since')
    limit = request.args.get('limit')
    desc = request.args.get('desc')
    thread = Thread.get_by_slug_or_id(slug_or_id)
    posts = []
    if not thread:
        return json_response({'message': 'Thread not found'}, 404)
    if sort == "flat" or sort is None:
        posts = Thread.get_posts_flat_sorted(thread['id'], since, limit, desc)
    elif sort == "tree":
        posts = Thread.get_posts_tree_sorted(thread['id'], since, limit, desc)
    elif sort == "parent_tree":
        posts = Thread.get_posts_parent_tree_sorter(thread['id'], since, limit, desc)
    for post in posts:
        post['created'] = format_time(post['created'])
    return json_response(posts, 200)


@thread.route('/<slug_or_id>/vote', methods=['POST'])
def vote_thread(slug_or_id):
    post_data = request.get_json()
    thread_id, user_id = Thread.check_user_and_thread(thread_slug_or_id=slug_or_id, nickname=post_data['nickname'])
    if not user_id and not thread_id:
        return json_response({'message': 'Thread OR USER not found'}, 404)
    thread = Vote.vote_for_thread(user_id, post_data['voice'], thread_id)
    thread['created'] = format_time(thread['created'])
    return json_response(thread, 200)
