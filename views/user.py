from flask import Blueprint

user = Blueprint('user', __name__)


@user.route('/<nickname>/create', methods=['POST'])
def create_user(nickname):
    return nickname


@user.route('/<nickname>/profile', methods=['GET'])
def get_user_profile(nickname):
    return nickname


@user.route('/<nickname>/profile', methods=['GET'])
def edit_user_profile(nickname):
    return nickname
