import pytz as pytz
from flask import json, Response


def format_time(time):
    zone = pytz.timezone('Europe/Moscow')
    if time.tzinfo is None:
        time = zone.localize(time)
    utc_time = time.astimezone(pytz.utc)
    utc_str = utc_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
    utc_str = utc_str[:-3] + 'Z'
    return utc_str


def json_response(payload, status_code):
    return Response(
        response=json.dumps(payload),
        status=status_code,
        mimetype="application/json"
    )
