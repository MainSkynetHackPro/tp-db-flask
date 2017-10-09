from flask import Blueprint, request

from models.user import User

user = Blueprint('user', __name__)


@user.route('/<nickname>/create', methods=['POST'])
def create_user(nickname):
    user = User()
    user.load_from_json(request.get_json())
    user.nickname = nickname
    user.create()
    return nickname


@user.route('/<nickname>/profile', methods=['GET'])
def get_user_profile(nickname):
    return nickname


@user.route('/<nickname>/profile', methods=['GET'])
def edit_user_profile(nickname):
    return nickname
