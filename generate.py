import os
import shutil
import codecs

from mako.template import Template
from mako.lookup import TemplateLookup


src = 'src'
target ='build'
media = os.path.abspath(os.path.join(target, 'media'))


def generate():
    if not os.path.exists(target):
        os.mkdir(target)


    lookup = TemplateLookup(directories=['.'])

    for root, dirs, files in os.walk(src):
        for file in files:
            ext = os.path.splitext(file)[-1]
            path = os.path.join(root, file)

            if ext == '.mako':
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
            else:
                shutil.copyfile(path, file_target)

    # media
    if os.path.exists(media):
        shutil.rmtree(media)
    shutil.copytree('media', media)


if __name__ == '__main__':
    generate()
