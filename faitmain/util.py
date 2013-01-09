import json
import urllib2
import cgi
import unicodedata

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


def hilite(node):
    lexer = 'text'
    if 'classes' in node.attributes:
        classes = node.attributes['classes']
        if len(classes) == 2:
            lexer = node.attributes['classes'][-1]

    code = node.astext()
    lexer = get_lexer_by_name(lexer)
    formatter = HtmlFormatter(style='colorful')
    return highlight(code, lexer, formatter)


def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if
                   unicodedata.category(c) != 'Mn'))


def _notag(text):
    return cgi.escape(text)


def shorten(url, server, password):
    req = urllib2.Request(server, headers={'X-Short': password})
    req.get_method = lambda: 'POST'
    req.add_data(url)
    res = urllib2.urlopen(req).read()
    res = json.loads(res)
    return server + '/' + res['short']
