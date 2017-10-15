from flask import Blueprint, request, json, Response

from models.user import User

view = Blueprint('user', __name__)


@view.route('/<nickname>/create', methods=['POST'])
def create_user(nickname):
    json_data = request.get_json()
    users_list = User.get_users_with_nickname_or_email(nickname=nickname, email=json_data['email'])
    if users_list:
        return Response(
            json.dumps(User.serizlize_list(users_list)),
            status=409,
            mimetype="application/json"
        )
    user = User()
    user.load_from_dict(json_data)
    user.nickname.val(nickname)
    user.save()
    return Response(
        response=json.dumps(user.serialize()),
        status=201,
        mimetype="application/json"
    )


@view.route('/<nickname>/profile', methods=['GET'])
def get_user_profile(nickname):
    user = User.get_user_by_nickname(nickname=nickname)
    if user:
        return Response(
            response=json.dumps(user),
            status=200,
            mimetype="application/json"
        )
    return Response(
        response=json.dumps(
            {
                "message": "Can't find user with nickname {0}".format(nickname)
            }),
        status=404,
        mimetype="application/json"
    )


@view.route('/<nickname>/profile', methods=['POST'])
def edit_user_profile(nickname):
    json_data = request.get_json()
    user = User.get_user_by_nickname(nickname)
    params = {}

    if not user:
        return Response(
            response=json.dumps(
                {"message": "Can't find user with nickname {0}".format(nickname)}
            ),
            status=404,
            mimetype="application/json"
        )
    if 'nickname' in json_data.keys() and user['nickname'] != json_data['nickname']:
        params['nickname'] = json_data['nickname']
    if 'email' in json_data.keys() and user['email'] != json_data['email']:
        params['email'] = json_data['email']

    if params:
        users_list = User.get_users_by_or_attributes(params)
        if users_list:
            return Response(
                response=json.dumps({
                    "message": "Fields conflict"
                }),
                status=409,
                mimetype="application/json")
    if len(json_data) > 0:
        user_data = User.update_by_nickname(nickname, json_data)
    else:
        user_data = user
    return Response(
        response=json.dumps(user_data),
        status=200,
        mimetype="application/json"
    )
