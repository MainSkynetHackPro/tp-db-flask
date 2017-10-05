from flask import Blueprint

service = Blueprint('service', __name__)


@service.route('/clear', methods=['POST'])
def clear_db():
    return str(1)


@service.route('/status', methods=['GET'])
def get_db_status():
    return str(1)
