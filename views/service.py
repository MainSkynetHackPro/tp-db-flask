from flask import Blueprint, Response

from models.forum import Forum
from models.user import User
from modules.dbconector import DbConnector

service = Blueprint('service', __name__)


@service.route('/clear', methods=['POST'])
def clear_db():
    sql_table = """
        TRUNCATE TABLE "{0}";
    """
    sql = ""
    for item in (User, Forum):
        sql += sql_table.format(item.tbl_name)

    DbConnector().execute_set(sql)
    return Response(response="", status=200)

@service.route('/status', methods=['GET'])
def get_db_status():
    return str(1)
