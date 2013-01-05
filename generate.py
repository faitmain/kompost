import os
import shutil
import codecs
import cgi
import urllib2
import json
import sys
import socket
import unicodedata
from collections import defaultdict

from docutils.core import publish_doctree

from mako.template import Template
from mako.lookup import TemplateLookup

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


socket.setdefaulttimeout(1)


def hilite(node):
    lexer = 'text'
    if 'classes' in node.attributes:
        classes = node.attributes['classes']
        if len(classes) == 2:
            lexer = node.attributes['classes'][-1]

    code = node.astext()
    lexer = get_lexer_by_name(lexer)
    formatter = HtmlFormatter(
                              style='colorful')
    return highlight(code, lexer, formatter)


_SERVER = 'http://short.faitmain.org'
_KEY = 'booba82'

def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if
                   unicodedata.category(c) != 'Mn'))

src = 'src'
target ='build'
media = os.path.abspath(os.path.join(target, 'media'))
_GENERIC = os.path.join(src, 'generic.mako')
_CATS = os.path.join(src, 'category.mako')
_ICONS = ('pen.png', 'info.png', 'thumbsup.png',
          'right.png', 'flash.png')
_METADATA = os.path.join(target, 'metadata.json')


def _notag(text):
    return cgi.escape(text)


def shorten(url):
    req = urllib2.Request(_SERVER, headers={'X-Short': _KEY})
    req.get_method = lambda: 'POST'
    req.add_data(url)
    res = urllib2.urlopen(req).read()
    res = json.loads(res)
    return _SERVER + '/' + res['short']



_INDEX = defaultdict(dict)


def _index(document, title, name, value):
    _INDEX[document + ':' + title][name] = value


def _save_index():
    if os.path.exists(_METADATA):
        with open(_METADATA) as f:
            metadata = json.loads(f.read())
    else:
        metadata = {}

    metadata.update(_INDEX)

    with open(_METADATA, 'w') as f:
        f.write(json.dumps(metadata))


def _tree(node, document, title):
    """Renders a node in HTML.
    """
    text = []
    klass = node.__class__.__name__
    if klass == 'transition':
        text.append('<hr/>')
    elif klass == 'system_message':
        pass
    elif klass == 'paragraph':
        text.append('<p>')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</p>')
    elif klass == 'Text':
        text.append(node.astext())
    elif klass == 'literal_block':
        text.append('<div class="syntax rounded">')
        text.append(hilite(node))
        text.append('</div>')
    elif klass == 'note':
        text.append('<div class="well note">')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</div>')
    elif klass == 'emphasis':
        text.append('<em>')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</em>')
    elif klass == 'strong':
        text.append('<strong>')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</strong>')
    elif klass == 'image':
        nolegend = False
        if node.hasattr('uri'):
            uri = node['uri']
            file_ = os.path.split(uri)[-1]
            if file_ in _ICONS:
                class_ = 'subst'
                nolegend = True
            else:
                text.append('<div>')
                class_ = 'centered'
            text.append('<img class="%s" src="%s">' % (class_, uri))
        else:
            text.append('<div>')
            text.append('<img class="centered">')

        for child in node.children:
            text.append(_tree(child, document, title))

        text.append('</img>')
        if not nolegend and 'alt' in node:
            text.append('<span class="legend">')
            text.append(node['alt'])
            text.append('</span>')
            text.append('</div>')

    elif klass == 'reference':
        if node.hasattr('refid'):
            text.append('<a href="#%s">' % node['refid'])
        elif node.hasattr('refuri'):
            refuri = node['refuri']
            if 'wikipedia.org' in refuri:
                text.append('<a href="%s" class="wikipedia">' % refuri)
            else:
                #if 'faitmain.org' not in refuri and not refuri.startswith('/'):
                #    try:
                #        refuri = shorten(refuri)
                #    except urllib2.URLError:
                #        pass

                text.append('<a href="%s">' % refuri)
        else:
            text.append('<a>')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</a>')
    elif klass == 'target':
        # ??
        pass
    elif klass == 'section':
        text.append('<h2>%s</h2>' % node.children[0][0].astext())
        for child in node.children[1:]:
            text.append(_tree(child, document, title))
    elif klass == 'bullet_list':
        text.append('<ul>')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</ul>')
    elif klass == 'enumerated_list':
        text.append('<ol>')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</ol>')
    elif klass == 'substitution_definition':
        #uri = node.children[0].attributes['uri']
        #text.append('<img class="subst" src="%s"></img>' % uri)
        pass
    elif klass == 'list_item':
        text.append('<li>')
        for child in node.children:
            text.append(_tree(child, document, title))
        text.append('</li>')
    elif klass == 'docinfo':
        # reading metadata
        for child in node.children:
            text.append(_tree(child, document, title))
    elif klass == 'author':
        value = node.astext()
        _index(document, title, 'author', value)
        author_id = strip_accents(value).lower()
        author_id = author_id.replace(' ', '_')
        text.append('<img class="subst" '
                    'src="http://cnd.faitmain.org/media/pen.png">')
        text.append('</img>')
        text.append('<a href="/auteurs/%s.html">%s</a>' % (author_id,
                                                           value))
    elif klass == 'date':
        # XXX
        pass
    elif klass == 'field':
        name = node.children[0].astext()
        value = node.children[1].astext()
        if name == 'category':
            text.append('<img class="subst" '
                        'src="http://cnd.faitmain.org/media/info.png">')
            text.append('</img>')
            cats = value.split(',')
            _index(document, title, name, cats)

            cats = ['<a href="/%s.html">%s</a>' % (cat, cat.capitalize())
                    for cat in cats]
            text.append(' | '.join(cats))
        elif name == 'level':
            _index(document, title, name, value)

            text.append('<img class="subst" '
                        'src="http://cnd.faitmain.org/media/flash.png">')
            text.append('</img>')
            text.append('<strong>Niveau</strong>: %s' % value.capitalize())
    else:
        raise NotImplementedError(node)

    return ' '.join(text)


_FOOTER = """
.. |pen| image:: http://cnd.faitmain.org/media/pen.png
.. |info| image:: http://cnd.faitmain.org/media/info.png
.. |thumbsup| image:: http://cnd.faitmain.org/media/thumbsup.png
.. |right| image:: http://cnd.faitmain.org/media/right.png
.. |flash| image:: http://cnd.faitmain.org/media/flash.png

"""


def generate():
    if not os.path.exists(target):
        os.mkdir(target)


    lookup = TemplateLookup(directories=['.'])

    for root, dirs, files in os.walk(src):
        for file in files:
            ext = os.path.splitext(file)[-1]
            path = os.path.join(root, file)

            if ext in ('.mako' , '.un~'):
                continue

            # getting read of '/src
            location = path[len('src/'):]
            file_target = os.path.join(target, location)
            target_dir = os.path.dirname(file_target)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            if ext == '.html':
                mytemplate = Template(filename=path, lookup=lookup)
                print 'Generating %r' % file_target

                with codecs.open(file_target, 'w', encoding='utf8') as f:
                    f.write(mytemplate.render())
            elif ext == '.rst':
                # generating the tree, then creating a mako document
                with open(path) as f:
                    content = f.read() + _FOOTER
                    doctree = publish_doctree(content)

                title = doctree.children[0].astext()
                file_target = os.path.splitext(file_target)[0] + '.html'
                url_target = file_target[len(target):]

                paragraphs = ['<p>%s</p>' % _tree(text, url_target, title)
                              for text in doctree.children[1:]]

                mytemplate = Template(filename=_GENERIC, lookup=lookup)

                print 'Generating %r' % file_target

                with codecs.open(file_target, 'w', encoding='utf8') as f:
                    f.write(mytemplate.render(body='\n'.join(paragraphs),
                                              title=title))

                _save_index()
            else:
                print 'Copying %r' % file_target
                shutil.copyfile(path, file_target)

    # media
    if os.path.exists(media):
        shutil.rmtree(media)
    shutil.copytree('media', media)

    # building category pages now
    categories = defaultdict(list)

    for key, index in _INDEX.items():
        path, title = key.split(':')
        for key, value in index.items():
            if key != 'category':
                continue
            for cat in value:
                categories[cat].append((path, title))

    for wanted in ('electronique', 'informatique', 'art', 'cuisine',
                   'ecologie'):
        if wanted in categories:
            continue
        categories[wanted] = []

    for cat, paths in categories.items():
        print 'Generating category %r' % cat
        file_target = os.path.join(target, cat + '.html')

        mytemplate = Template(filename=_CATS, lookup=lookup)

        with codecs.open(file_target, 'w', encoding='utf8') as f:
            f.write(mytemplate.render(paths=paths, title=cat.capitalize()))


if __name__ == '__main__':
    generate()
