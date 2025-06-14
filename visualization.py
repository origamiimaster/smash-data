"""This will include a live visualization of matches as they are processed so I can better understand why some
mistakes occur.  """

from flask import Flask, url_for, request
from typing import Optional
import requests
from markupsafe import escape
from elastic_client import get_set_by_set_id, get_event_by_event_id

app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def hello_world() -> str:
    """Basic function for the base url"""
    # return f"Hello World. {url_for('static', filename='index.html')}"
    return "Hello World"


# @app.route('/user/<username>')
# def get_user(username):
#     return f"User: {escape(username)}"


@app.route('/sets/<set_id>')
def get_set_info(set_id) -> Optional[set]:
    """Thingy"""
    my_set = get_set_by_set_id(set_id)['_source']
    # print(my_set)
    if my_set is None:
        return {"An error occurred"}
    return my_set


@app.route('/events/<event_id>')
def get_event_info(event_id) -> Optional[set]:
    """Get's the event by the id if it exists."""
    my_event = get_event_by_event_id(event_id)['_source']
    if my_event is None:
        return {"An error occurred"}
    return my_event


@app.route('/api/event/<query_str>')
def api_event_query(query_str) -> object:
    """Query the legacy event api for something"""
    body = requests.get(f'https://api.smash.gg/event/{query_str}')
    return str(body.json())


@app.route('/api/set/<query_str>')
def api_set_query(query_str) -> object:
    """Query the legacy event api for something"""
    body = requests.get(f'https://api.smash.gg/set/{query_str}')
    return str(body.json())
