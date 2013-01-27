import os
import json
from collections import defaultdict


_INDEX = defaultdict(dict)


def get_index():
    items = _INDEX.items()
    items.sort()
    return items

def get_document_index(document, title):
    return _INDEX[document + ':' + title]


def index(document, title, name, value, append=False):
    key = document + ':' + title

    if append:
        current = _INDEX[key].get(name, [])
        current.append(value)
        value = current

    _INDEX[key][name] = value


def save_index(metadata):
    if os.path.exists(metadata):
        with open(metadata) as f:
            data = json.loads(f.read())
    else:
        data = {}

    data.update(_INDEX)

    with open(metadata, 'w') as f:
        f.write(json.dumps(data))
