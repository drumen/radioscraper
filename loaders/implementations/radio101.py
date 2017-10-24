from datetime import datetime
from requests import Request


def _timestamp():
    return int(datetime.now().timestamp() * 1000)


def form_request():
    return Request("GET", 'http://138.201.248.219:8006/stats', params={
        'sid': 1,
        'json': 1,
        '_': _timestamp(),
    })


def parse_response(response):
    data = response.json()
    author, title = [
        data[0]['author'],
        data[0]['title'],
    ]

    if author and title:
        return [author, title]
