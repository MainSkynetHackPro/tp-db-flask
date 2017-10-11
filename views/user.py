from flask import Blueprint, request, json

from models.user import User

user = Blueprint('user', __name__)


@user.route('/<nickname>/create', methods=['POST'])
def create_user(nickname):
    json_data = request.get_json()
    users_list = User().get_list_or({'nickname': nickname, 'email': json_data['email']})
    if users_list:
        return json.dumps(User.serizlize_list(users_list)), 409

    user = User()
    user.load_from_json(json_data)
    user.nickname.val(nickname)
    user.save()
    return json.dumps(user.serialize()), 201


@user.route('/<nickname>/profile', methods=['GET'])
def get_user_profile(nickname):
    user = User().get({'nickname': nickname})
    if user.exists:
        return json.dumps(user.serialize())
    return json.dumps(
        {
            "message": "Can't find user with nickname {0}".format(nickname)
        }
    )


@user.route('/<nickname>/profile', methods=['POST'])
def edit_user_profile(nickname):
    user = User().get({'nickname': nickname})
    user.load_from_json(request.get_json())
    user.save()
    return json.dumps(user.serialize())
