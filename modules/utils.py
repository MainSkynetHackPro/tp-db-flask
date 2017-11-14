import pytz as pytz


def format_time(time):
    zone = pytz.timezone('Europe/Moscow')
    if time.tzinfo is None:
        time = zone.localize(time)
    utc_time = time.astimezone(pytz.utc)
    utc_str = utc_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
    utc_str = utc_str[:-3] + 'Z'
    return utc_str
