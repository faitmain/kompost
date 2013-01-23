import os
import json
from collections import defaultdict


_INDEX = defaultdict(dict)


def get_index():
    items = _INDEX.items()
    items.sort()
    return items


def index(document, title, name, value):
    _INDEX[document + ':' + title][name] = value


def save_index(metadata):
    if os.path.exists(metadata):
        with open(metadata) as f:
            data = json.loads(f.read())
    else:
        data = {}

    data.update(_INDEX)

    with open(metadata, 'w') as f:
        f.write(json.dumps(data))
