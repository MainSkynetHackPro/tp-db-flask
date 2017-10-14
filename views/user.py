from flask import Blueprint, request, json, Response

from models.user import User

view = Blueprint('user', __name__)


@view.route('/<nickname>/create', methods=['POST'])
def create_user(nickname):
    json_data = request.get_json()
    users_list = User().get_list_or({'nickname': nickname, 'email': json_data['email']})
    if users_list:
        return Response(json.dumps(User.serizlize_list(users_list)),
                        status=409,
                        mimetype="application/json")
    user = User()
    user.load_from_dict(json_data)
    user.nickname.val(nickname)
    user.save()
    return Response(response=json.dumps(user.serialize()),
                    status=201,
                    mimetype="application/json")


@view.route('/<nickname>/profile', methods=['GET'])
def get_user_profile(nickname):
    user = User().get({'nickname': nickname})
    if user.exists:
        return json.dumps(user.serialize()), 200
    return json.dumps({
        "message": "Can't find user with nickname {0}".format(nickname)
    }), 404


@view.route('/<nickname>/profile', methods=['POST'])
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
        user.load_from_dict(request.get_json())
        user.save()
        return json.dumps(user.serialize())
    else:
        return json.dumps({
            "message": "Can't find user with nickname {0}".format(nickname)
        }), 404
