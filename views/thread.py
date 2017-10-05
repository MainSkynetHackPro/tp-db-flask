from flask import Blueprint

thread = Blueprint('thread', __name__)


@thread.route('/<slug_or_id>/create', methods=['POST'])
def create_thread(slug_or_id):
    return str(1)


@thread.route('/<slug_or_id>/details', methods=['GET'])
def get_thread_details(slug_or_id):
    return str(1)


@thread.route('/<slug_or_id>/details', methods=['POST'])
def update_thread(slug_or_id):
    return str(1)


@thread.route('/<slug_or_id>/posts', methods=['GET'])
def get_thread_messages(slug_or_id):
    return str(1)


@thread.route('/<slug_or_id>/vote', methods=['POST'])
def vote_thread(slug_or_id):
    return str(1)
