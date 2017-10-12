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
    test = User.get_sql_generator('select')
    test.where({'about': 'about'})
    test.where_not({'id': 11})
    return json.dumps(test.execute())

    user = User().get({'nickname': nickname})
    if user.exists:
        return json.dumps(user.serialize()), 200
    return json.dumps({
        "message": "Can't find user with nickname {0}".format(nickname)
    }), 404


@user.route('/<nickname>/profile', methods=['POST'])
def edit_user_profile(nickname):
    json_data = request.get_json()
    params = {}
    if 'nickname' in json_data.keys():
        params['nickname'] = json_data['nickname']
    if 'email' in json_data.keys():
        params['email'] = json_data['email']

    users_list = User().get_list_or(params)
    if users_list:
        return json.dumps({
            "message": "Can't find user with nickname {0}".format(nickname)
        }), 409
    user = User().get({'nickname': nickname})
    if user.exists:
        user.load_from_json(request.get_json())
        user.save()
        return json.dumps(user.serialize())
    else:
        return json.dumps({
            "message": "Can't find user with nickname {0}".format(nickname)
        }), 404
