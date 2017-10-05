from flask import Blueprint, json

forum = Blueprint('forum', __name__)


@forum.route('/create', methods=['POST'])
def create_forum():
    return 'created'


@forum.route('/<slug>/create', methods=['POST'])
def create_branch(slug):
    return slug


@forum.route('/<slug>/details', methods=['GET'])
def get_forum_details(slug):
    return slug


@forum.route('/<slug>/threads', methods=['GET'])
def get_threads_list(slug):
    return slug


@forum.route('/<slug>/users', methods=['GET'])
def get_forum_users(slug):
    return slug


@forum.route('/<id>/details', methods=['GET'])
def get_post_details(id):
    return id


@forum.route('/<id>/details', methods=['POST'])
def change_post_message(id):
    return id



