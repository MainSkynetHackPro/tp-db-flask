from flask import Blueprint, request

from models.post import Post
from modules.utils import json_response

post = Blueprint('post', __name__)


@post.route('/<post_id>/details', methods=['GET'])
def create_thread(post_id):
    related = request.args.get('related')
    post = Post.get_info(post_id, related)
    if not post['post']:
        return json_response({'message': 'post not found'}, 404)
    return json_response(post, 200)


@post.route('/<post_id>/details', methods=['POST'])
def update_post(post_id):
    update_data = request.get_json()
    post = Post.get_post(post_id)
    if not post:
        return json_response({'message': 'post not found'}, 404)
    post = Post.update_post(post['id'], update_data, post)

    return json_response(post, 200)
