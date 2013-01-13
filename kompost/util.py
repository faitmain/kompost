import json
import urllib2
import cgi
import unicodedata
import logging

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from kompost import logger


LOG_FMT = r"[%(levelname)s] %(message)s"
LOG_DATE_FMT = r"%Y-%m-%d %H:%M:%S"


def configure_logger(loglevel=logging.INFO, output="-"):
    logger.setLevel(loglevel)
    if output == "-":
        h = logging.StreamHandler()
    else:
        h = logging.FileHandler(output)
    fmt = logging.Formatter(LOG_FMT, LOG_DATE_FMT)
    h.setFormatter(fmt)
    logger.addHandler(h)


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
    logger.debug('Shortening %r' % url)
    req = urllib2.Request(server, headers={'X-Short': password})
    req.get_method = lambda: 'POST'
    req.add_data(url)
    try:
        res = urllib2.urlopen(req).read()
    except urllib2.URLError:
        logger.debug('Error on the call')
        return url
    res = json.loads(res)
    res = server + '/' + res['short']
    logger.debug('Shortened to %r' % res)
    return res