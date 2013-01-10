import os
import codecs
import urllib2

from faitmain.index import save_index, index
from faitmain.util import shorten, hilite, strip_accents
from faitmain import logger

from docutils.core import publish_doctree
from mako.template import Template
from mako.lookup import TemplateLookup


_FOOTER = """
.. |pen| image:: http://cnd.faitmain.org/media/pen.png
.. |info| image:: http://cnd.faitmain.org/media/info.png
.. |thumbsup| image:: icon-thumbs-up
.. |right| image:: http://cnd.faitmain.org/media/right.png
.. |flash| image:: http://cnd.faitmain.org/media/flash.png
.. |infosign| image:: icon-info-sign
"""


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
                    refuri = shorten(refuri, config['shortener_server'],
                                     config['shortener_key'])
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
        index(document, title, 'author', value)
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
            index(document, title, name, cats)

            cats = ['<a href="/%s.html">%s</a>' % (cat, cat.capitalize())
                    for cat in cats]
            text.append(' | '.join(cats))
        elif name == 'level':
            index(document, title, name, value)

            text.append('<img class="subst" '
                        'src="%s/media/flash.png">' % cnd)
            text.append('</img>')
            text.append('<strong>Niveau</strong>: %s' % value.capitalize())
        elif name == 'translator':
            index(document, title, name, value)

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


class RestructuredText(object):

    exts = ('.rst',)

    def __init__(self, config):
        self.config = config
        self.lookup = TemplateLookup(directories=['.'])

    def __call__(self, path, target, url_target, **options):
        target = os.path.splitext(target)[0] + '.html'

        with open(path) as f:
            content = f.read() + _FOOTER
            doctree = publish_doctree(content)

        title = doctree.children[0].astext()
        target = os.path.splitext(target)[0] + '.html'

        paragraphs = ['<p>%s</p>' % _tree(text, url_target, title,
                                          self.config)
                      for text in doctree.children[1:]]

        mytemplate = Template(filename=self.config['generic'],
                              lookup=self.lookup)

        logger.info('Generating %r' % target)

        with codecs.open(target, 'w', encoding='utf8') as f:
            f.write(mytemplate.render(body='\n'.join(paragraphs),
                                      title=title, **options))

        save_index(self.config['metadata'])
