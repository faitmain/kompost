import os
import shutil
import codecs

from docutils.core import publish_doctree

from mako.template import Template
from mako.lookup import TemplateLookup


src = 'src'
target ='build'
media = os.path.abspath(os.path.join(target, 'media'))
_GENERIC = os.path.join(src, 'generic.mako')


def _tree(node):
    """Renders a node in HTML.
    """
    text = []
    klass = node.__class__.__name__
    if klass == 'paragraph':
        text.append('<p>')
        for child in node.children:
            text.append(_tree(child))
        text.append('</p>')
    elif klass == 'Text':
        text.append(node.astext())
    elif klass == 'note':
        text.append('<div class="well">')
        for child in node.children:
            text.append(_tree(child))
        text.append('</div>')
    elif klass == 'strong':
        text.append('<strong>')
        for child in node.children:
            text.append(_tree(child))
        text.append('</strong>')
    elif klass == 'image':
        if node.hasattr('uri'):
            text.append('<img src="%s">' % node['uri'])
        else:
            text.append('<img>')
        for child in node.children:
            text.append(_tree(child))
        text.append('</img>')

    elif klass == 'reference':
        if node.hasattr('refid'):
            text.append('<a href="#%s">' % node['refid'])
        elif node.hasattr('refuri'):
            text.append('<a href="%s">' % node['refuri'])
        else:
            text.append('<a>')
        for child in node.children:
            text.append(_tree(child))
        text.append('</a>')
    elif klass == 'target':
        # ??
        pass
    elif klass == 'section':
        text.append('<h2>%s</h2>' % node.children[0][0].astext())
        for child in node.children[1:]:
            text.append(_tree(child))
    elif klass == 'bullet_list':
        text.append('<ul>')
        for child in node.children:
            text.append(_tree(child))
        text.append('</ul>')
    elif klass == 'list_item':
        text.append('<li>')
        for child in node.children:
            text.append(_tree(child))
        text.append('</li>')
    else:
        raise NotImplementedError(klass)

    return ' '.join(text)


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
            print 'Generating %r' % file_target
            target_dir = os.path.dirname(file_target)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            if ext == '.html':
                mytemplate = Template(filename=path, lookup=lookup)

                with codecs.open(file_target, 'w', encoding='utf8') as f:
                    f.write(mytemplate.render())
            elif ext == '.rst':
                # generating the tree, then creating a mako document
                with open(path) as f:
                    doctree = publish_doctree(f.read())

                title = doctree.children[0].astext()

                paragraphs = ['<p>%s</p>' % _tree(text)
                              for text in doctree.children[1:]]

                mytemplate = Template(filename=_GENERIC, lookup=lookup)

                file_target = os.path.splitext(file_target)[0] + '.html'
                with codecs.open(file_target, 'w', encoding='utf8') as f:
                    f.write(mytemplate.render(body='\n'.join(paragraphs),
                                              title=title))


            else:
                shutil.copyfile(path, file_target)

    # media
    if os.path.exists(media):
        shutil.rmtree(media)
    shutil.copytree('media', media)


if __name__ == '__main__':
    generate()
