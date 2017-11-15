from flask import Blueprint, request, json, Response

from models.dbmodel import DbModel
from models.user import User
from modules.utils import json_response

view = Blueprint('user', __name__)


@view.route('/<nickname>/create', methods=['POST'])
def create_user(nickname):
    user, status = User().create_by_nickname(nickname, payload=request.get_json())
    return json_response(
        user,
        status
    )


@view.route('/<nickname>/profile', methods=['GET'])
def get_user_profile(nickname):
    user = User().get_by_nickname(nickname)
    if not user:
        return json_response(
            {
                'message': 'Failed to find user with nickname = {0}'.format(nickname)
            },
            404
        )
    return json_response(user, 200)


@view.route('/<nickname>/profile', methods=['POST'])
def edit_user_profile(nickname):
    user, status = User().update_by_nickname(nickname, payload=request.get_json())
    if status == DbModel.NOT_FOUND:
        return json_response(
            {
                'message': 'Failed to find user with nickname = {0}'.format(nickname)
            }, status
        )
    if status == DbModel.CONFLICTS:
        return json_response(
            {
                'message': 'Conflict with user {0}'.format(user[0]['nickname'])
            },
            DbModel.CONFLICTS
        )
    return json_response(user, status)
