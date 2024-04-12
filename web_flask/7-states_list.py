#!/usr/bin/python3
"""
Simple module that starts a Flask web application
Starting to display formatted text and conditional message
Addind basic template
"""
from flask import Flask, render_template
from models import storage
from models.state import State

app = Flask(__name__)


@app.teardown_appcontext
def handle_appcontext(self):
    """
    Method for handling app context
    """
    storage.close()


@app.route('/states_list', strict_slashes=False)
def list_states():
    """
    Displays 7-states_list html page
    """
    states = storage.all(State).values()
    return render_template('7-states_list.html', states=states)


if __name__ == "__main__":
    """ app listening on host 0.0.0.0 and port 5000 """
    app.run(host='0.0.0.0', port='5000')
