# -*- encoding: utf8 -*-
import os
import codecs
import urllib2

from kompost.index import save_index, index, get_document_index
from kompost.util import shorten, hilite, str2authorid
from kompost import logger

from docutils.core import publish_doctree

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import RichTraceback


_FOOTER = """

.. |pen| image:: http://cnd.faitmain.org/media/pen.png
.. |info| image:: http://cnd.faitmain.org/media/info.png
.. |thumbsup| image:: http://cnd.faitmain.org/media/thumbsup.png
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
    elif klass == 'block_quote':
        text.append('<blockquote>')
        for child in node.children:
            text.append(_tree(child, document, title, config))
        text.append('</blockquote>')
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
    elif klass == 'sidebar':
        text.append('<div class="alert alert-info">')
        text.append('<h4>%s</h4>' % node.children[0].astext())
        for child in node.children[1:]:
            text.append(_tree(child, document, title, config))
        text.append('</div>')

    elif klass == 'note':
        node.attributes['class'] = 'well note'
        text.extend(render_simple_tag(node, document, title, config,
                                      'div', strip_child=False))
    elif klass == 'warning':
        text.append('<div class="alert">')
        for child in node.children:
            text.append(_tree(child, document, title, config))
        text.append('</div>')
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
            offset = int((12-span) / 2.) - 1
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

    elif klass == 'figure':
        if len(node['classes']) > 0:
            floating = ' '.join(node['classes'])
        else:
            # let's use a row-fluid
            floating = None

        data = {}

        for child in node.children:
            klass = child.__class__.__name__
            data[klass] = child

        if 'image' not in data and 'reference' in data:
            data['image'] = data['reference'].children[0]

        # scaling
        if 'scale' in data['image']:
            scale = float(data['image']['scale'])
            span = 12. * (scale / 100.)
            offset = int((12-span) / 2.)
            span = 'span%d' % int(span)
            if offset > 0:
                span += ' offset%d' % offset
        else:
            span = 'span12'


        linked = 'reference' in data

        # image
        uri = data['image']['uri']
        file_ = os.path.split(uri)[-1]
        if file_ in config['icons']:
            class_ = 'subst'
            nolegend = True
        else:
            if floating is None:
                text.append('<div class="row-fluid">')

        # subdiv
        if floating is None:
            text.append('<div class="%s">' % span)
        else:
            text.append('<div class="%s">' % floating)

        # url
        if linked:
            refuri = data['reference']['refuri']

            if ('faitmain.org' not in refuri and not refuri.startswith('/')
                and int(config.get('shorten', 1)) == 1):
                refuri = shorten(refuri, config['shortener_server'],
                                 config['shortener_key'],
                                 config.get('amazon_tag'))

            text.append('<a href="%s">' % refuri)

        text.append('<img class="centered span12" src="%s"></img>' % uri)

        # caption
        if 'caption' in data:
            text.append('<span class="legend">')
            for child in data['caption'].children:
                text.append(_tree(child, document, title, config))
            text.append('</span>')

        if linked:
            text.append('</a>')

        text.append('</div>')

        if floating is None:
            text.append('</div>')

    elif klass == 'reference':  # link
        if node.hasattr('refid'):
            text.append('<a href="#%s">' % node['refid'])
        elif node.hasattr('refuri'):
            refuri = node['refuri']
            if 'wikipedia.org' in refuri:
                text.append('<a href="%s" class="wikipedia">' % refuri)
            else:
                if ('faitmain.org' not in refuri and not refuri.startswith('/')
                    and int(config.get('shorten', 1)) == 1):
                    refuri = shorten(refuri, config['shortener_server'],
                                     config['shortener_key'],
                                     config.get('amazon_tag'))
                text.append('<a href="%s">' % refuri)
        else:
            text.append('<a>')
        for child in node.children:
            text.append(_tree(child, document, title, config))
        text.append('</a>')
    elif klass == 'target':
        # ??
        pass
    elif klass == 'section':
        section_title = node.children[0][0].astext()
        id = node.attributes['ids'][0]
        index(document, title, 'sections', (section_title, id), append=True)
        text.append('<div id="%s" class="section">' % id)
        header = (u'<h2>%s <a class="headerlink" href="#%s"'
                  u'title="Lien vers cette section">\xb6</a></h2>')
        header = header % (section_title, id)
        text.append(header)

        for child in node.children[1:]:
            text.append(_tree(child, document, title, config))
        text.append('</div>')

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
        author_id = str2authorid(value)
        text.append('<img class="subst" '
                    'src="%s/media/pen.png">' % cnd)
        text.append('</img>')
        text.append('<a href="/auteurs/%s.html">%s</a>' % (author_id,
                                                           value))
    elif klass == 'date':
        index(document, title, 'date', node.astext())

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
            author_id = str2authorid(value)
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
        paths = target.split('/')
        is_article = len(paths) > 2

        paragraphs = ['<p>%s</p>' % _tree(text, url_target, title,
                                          self.config)
                      for text in doctree.children[1:]]

        # loading sections
        doc_sections = get_document_index(url_target, title).get('sections', [])
        mytemplate = Template(filename=self.config['generic'],
                              lookup=self.lookup)

        body = u'\n'.join(paragraphs)
        #body = body.replace(u'--', u'—')
        if is_article:
            index(url_target, title, 'body', body)

        logger.info('Generating %r' % target)

        with codecs.open(target, 'w', encoding='utf8') as f:
            try:
                f.write(mytemplate.render(body=body, title=title,
                                          doc_sections=doc_sections, **options))
            except Exception:
                traceback = RichTraceback()
                for filename, lineno, function, line in traceback.traceback:
                    print "File %s, line %s, in %s" % (filename,
                                                       lineno, function)
                    print line, "\n"
                raise

        paths = target.split('/')
        if is_article:
            index(url_target, title, 'volume', paths[1])

        save_index(self.config['metadata'])
