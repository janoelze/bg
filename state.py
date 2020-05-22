import json
from os import path

STATE = {}

def set_state(k, v):
    STATE[k] = v

def set_state_all(v):
    STATE = v

def get_state(k, default=None):
    if k in STATE:
        return STATE[k]
    else:
        return default

def get_state_all():
    return STATE

def persist_state():
    with open('data/state.json', 'w') as outfile:
        return json.dump(STATE, outfile)

def recover_state():
        if path.exists('data/state.json'):
            with open('data/state.json') as json_file:
                return json.load(json_file)
        else:
            return {
                'bpm': 120,
                'bars': CONFIG['bars']
            }
