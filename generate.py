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

                paragraphs = ['<p>%s</p>' % text.astext()
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
