from flask import Blueprint, request, json

from models.user import User

user = Blueprint('user', __name__)


@user.route('/<nickname>/create', methods=['POST'])
def create_user(nickname):
    user = User()
    user.load_from_json(request.get_json())
    user.nickname.val(nickname)
    user.save()
    return json.dumps(user.serialize())


@user.route('/<nickname>/profile', methods=['GET'])
def get_user_profile(nickname):
    user = User().get({'nickname': nickname})
    return json.dumps(user.serialize())


@user.route('/<nickname>/profile', methods=['POST'])
def edit_user_profile(nickname):
    user = User().get({'nickname': nickname})
    user.load_from_json(request.get_json())
    user.save()
    return json.dumps(user.serialize())
