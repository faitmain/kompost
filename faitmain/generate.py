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
import datetime
from ConfigParser import ConfigParser

import requests

from docutils.core import publish_doctree

from mako.template import Template
from mako.lookup import TemplateLookup

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from generate_pdf import generate as pdf

socket.setdefaulttimeout(1)


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



_INDEX = defaultdict(dict)


def _index(document, title, name, value):
    _INDEX[document + ':' + title][name] = value


def _save_index(metadata):
    if os.path.exists(metadata):
        with open(metadata) as f:
            data = json.loads(f.read())
    else:
        data = {}

    data.update(_INDEX)

    with open(metadata, 'w') as f:
        f.write(json.dumps(data))


SIMPLE_TAGS = {
    # node tagname: (html tagname, strip child?)
    'paragraph': ('p', False),
    'emphasis': ('em', False),
    'strong': ('strong', False),
    'literal': ('pre', False),
    'bullet_list': ('ul', False),
    'enumerated_list': ('ol', False),
    'list_item': ('li', True),
    'thead': ('thead', False),
    'tbody': ('tbody', False),
    'row': ('tr', False),
}


def render_simple_tag(node, document, title, config, tagname=None,
                      strip_child=False):
    """Render a tag using the simplest default method.

    If tagname is provided, it is used instead of the node.tagname attribute.
    If strip_child is True, then the (single) child is stripped and its
    children are rendered instead.

    """
    if tagname is None:
        tagname = node.tagname
    attributes = ['%s="%s"' % (attr, value) for attr, value in node.attlist()]
    rendered = ['<%s>' % tagname]
    if attributes:
        rendered[0] = '<%s %s>' % (tagname, " ".join(attributes))
    if node.children and strip_child:
        node = node.children[0]
    for child in node.children:
        rendered.append(_tree(child, document, title, config))
    rendered.append('</%s>' % tagname)
    return rendered


def _tree(node, document, title, config):
    """Renders a node in HTML.
    """
    cnd = config['cnd']
    text = []
    klass = node.__class__.__name__
    if klass == 'transition':
        text.append('<hr/>')
    elif klass == 'system_message':
        pass
    elif klass == 'paragraph':
        text.append('<p>')
        for child in node.children:
            text.append(_tree(child, document, title, config))
        text.append('</p>')
    elif klass == 'Text':
        text.append(node.astext())
    elif klass == 'literal_block':
        text.append('<div class="syntax rounded">')
        text.append(hilite(node))
        text.append('</div>')
    elif klass == 'note':
        node.attributes['class'] = 'well note'
        text.extend(render_simple_tag(node, document, title, config,
                                      'div', strip_child=False))
    elif klass == 'table':
        node.attributes['class'] = 'table'
        text.extend(render_simple_tag(node, document, title, config,
                                      'table', strip_child=True))

    elif klass == 'image':
        if node.get('uri').startswith('icon'):
            return '<i class="%s"></i>' % node.get('uri')

        nolegend = False
        if node.hasattr('scale'):
            span = 12. * (float(node['scale']) / 100.)
            offset = int((12-span) / 2.)
            span = 'span%d' % int(span)
            if offset > 0:
                span += ' offset%d' % offset
        else:
            span = 'span12'

        if node.hasattr('uri'):
            uri = node['uri']
            file_ = os.path.split(uri)[-1]
            if file_ in config['icons']:
                class_ = 'subst'
                nolegend = True
            else:
                text.append('<div class="row-fluid">')
                class_ = 'centered %s' % span

            text.append('<img class="%s" src="%s">' % (class_, uri))
        else:
            text.append('<div class="row-fluid">')
            text.append('<img class="centered %s">' % span)

        for child in node.children:
            text.append(_tree(child, document, title, config))

        text.append('</img>')
        if not nolegend and 'alt' in node:
            text.append('<span class="legend %s">' % span)
            text.append(node['alt'])
            text.append('</span>')
            text.append('</div>')

    elif klass == 'reference':  # link
        if node.hasattr('refid'):
            text.append('<a href="#%s">' % node['refid'])
        elif node.hasattr('refuri'):
            refuri = node['refuri']
            if 'wikipedia.org' in refuri:
                text.append('<a href="%s" class="wikipedia">' % refuri)
            else:
                if 'faitmain.org' not in refuri and not refuri.startswith('/'):
                    try:
                        refuri = shorten(refuri, config['shortener_server'],
                                         config['shortener_key'])
                    except urllib2.URLError:
                        pass
        else:
            text.append('<a>')
        for child in node.children:
            text.append(_tree(child, document, title, config))
        text.append('</a>')
    elif klass == 'target':
        # ??
        pass
    elif klass == 'section':
        text.append('<h2>%s</h2>' % node.children[0][0].astext())
        for child in node.children[1:]:
            text.append(_tree(child, document, title, config))
    elif klass == 'substitution_definition':
        #uri = node.children[0].attributes['uri']
        #text.append('<img class="subst" src="%s"></img>' % uri)
        pass
    elif klass == 'docinfo':
        # reading metadata
        for child in node.children:
            text.append(_tree(child, document, title, config))
    elif klass == 'author':
        value = node.astext()
        _index(document, title, 'author', value)
        author_id = strip_accents(value).lower()
        author_id = author_id.replace(' ', '_')
        text.append('<img class="subst" '
                    'src="%s/media/pen.png">' % cnd)
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
                        'src="%s/media/info.png">' % cnd)
            text.append('</img>')
            cats = value.split(',')
            _index(document, title, name, cats)

            cats = ['<a href="/%s.html">%s</a>' % (cat, cat.capitalize())
                    for cat in cats]
            text.append(' | '.join(cats))
        elif name == 'level':
            _index(document, title, name, value)

            text.append('<img class="subst" '
                        'src="%s/media/flash.png">' % cnd)
            text.append('</img>')
            text.append('<strong>Niveau</strong>: %s' % value.capitalize())
        elif name == 'translator':
            _index(document, title, name, value)

            text.append('<img class="subst" '
                        'src="%s/media/translation.png">' % cnd)
            text.append('</img>')
            author_id = strip_accents(value).lower()
            author_id = author_id.replace(' ', '_')
            msg = ('<strong>Traduction</strong>: '
                   '<a href="/auteurs/%s.html">%s</a>')
            text.append(msg % (author_id, value))

    elif klass == 'colspec':  # table colspec
        pass
    elif klass == 'entry':  # table entry
        tagname = 'td'
        if node.parent.parent.tagname == 'thead':
            tagname = 'th'
        text.extend(render_simple_tag(node, document, title, config,
                                      tagname, strip_child=True))
    elif klass in SIMPLE_TAGS:
        tagname, strip_child = SIMPLE_TAGS[klass]
        text.extend(render_simple_tag(node, document, title, config,
                                      tagname, strip_child=strip_child))
    else:
        raise NotImplementedError(node)

    return ' '.join(text)


_FOOTER = """
.. |pen| image:: http://cnd.faitmain.org/media/pen.png
.. |info| image:: http://cnd.faitmain.org/media/info.png
.. |thumbsup| image:: icon-thumbs-up
.. |right| image:: http://cnd.faitmain.org/media/right.png
.. |flash| image:: http://cnd.faitmain.org/media/flash.png
.. |infosign| image:: icon-info-sign
"""


def generate(config):
    sitemap = []
    target = config['target']
    src = config['src']

    if not os.path.exists(target):
        os.mkdir(target)

    lookup = TemplateLookup(directories=['.'])

    for root, dirs, files in os.walk(src):
        for file in files:
            ext = os.path.splitext(file)[-1]
            path = os.path.join(root, file)

            if ext in ('.mako', '.un~'):
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
                url_target = file_target[len(target):]

                with codecs.open(file_target, 'w', encoding='utf8') as f:
                    f.write(mytemplate.render())

                sitemap.append(url_target)
            elif ext == '.rst':
                # generating the tree, then creating a mako document
                with open(path) as f:
                    content = f.read() + _FOOTER
                    doctree = publish_doctree(content)

                title = doctree.children[0].astext()
                file_target = os.path.splitext(file_target)[0] + '.html'
                url_target = file_target[len(target):]

                paragraphs = ['<p>%s</p>' % _tree(text, url_target, title,
                    config)
                              for text in doctree.children[1:]]

                mytemplate = Template(filename=config['generic'], lookup=lookup)

                print 'Generating %r' % file_target

                with codecs.open(file_target, 'w', encoding='utf8') as f:
                    f.write(mytemplate.render(body='\n'.join(paragraphs),
                                              title=title))

                sitemap.append(url_target)
                _save_index(config['metadata'])
            else:
                print 'Copying %r' % file_target
                shutil.copyfile(path, file_target)

    # media
    media = config['media']

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

        mytemplate = Template(filename=config['cats'], lookup=lookup)
        sitemap.append('/%s.html' % cat)

        with codecs.open(file_target, 'w', encoding='utf8') as f:
            f.write(mytemplate.render(paths=paths, title=cat.capitalize()))

    # creating sitemap
    sitemap_file = os.path.join(target, 'sitemap.json')
    print 'Generating sitemap at %r' % sitemap_file
    now = datetime.datetime.now().isoformat()

    urlset = [{'loc': loc, 'lastmod': now,
               'changefreq': 'monthly',
               'priority': 0.1} for loc in sitemap]

    with open(sitemap_file, 'w') as f:
        f.write(json.dumps({'urlset': urlset}))

    # asking Trouvailles to index the web site
    print 'Indexing the whole website'
    url = config['search_server']
    data = {'sitemap': config['sitemap']}
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        print 'Indexation failed'
        print r.status_code
        print r.content


def main():
    config = ConfigParser()
    config.read('faitmain.ini')
    config = dict(config.items('faitmain'))
    target = config['target']
    src = config['src']

    config['media'] = os.path.abspath(os.path.join(target, 'media'))
    config['generic'] = os.path.join(src, 'generic.mako')
    config['cats'] = os.path.join(src, 'category.mako')
    config['icons'] = ('pen.png', 'info.png', 'thumbsup.png',
                      'right.png', 'flash.png')
    config['metadata'] = os.path.join(target, 'metadata.json')
    generate(config)
    pdf(config)


if __name__ == '__main__':
    main()
