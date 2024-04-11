#!/usr/bin/python3
from flask import Flask, render_template
from models import storage
from models.state import State

app = Flask(__name__)


@app.teardown_appcontext
def teardown_appcontext(exception=None):
    """Close the current storage (DBStorage) session."""
    storage.close()


@app.route('/states_list', strict_slashes=False)
def states_list():
    """Display a HTML page with a list of all State objects sorted by name."""
    states = storage.all(State).values()
    sorted_states = sorted(states, key=lambda state: state.name)
    return render_template('states_list.html', sorted_states=sorted_states)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
