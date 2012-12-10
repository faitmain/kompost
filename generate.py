import os
import shutil

from mako.template import Template
from mako.lookup import TemplateLookup


def generate():
    target = os.path.join(os.path.dirname(__file__), 'build')
    if not os.path.exists(target):
        os.mkdir(target)

    lookup = TemplateLookup(directories=['.'])

    for file in os.listdir('.'):
        if not file.endswith('.html'):
            continue

        mytemplate = Template(filename=file, lookup=lookup)

        with open(os.path.join(target, file), 'w') as f:
            f.write(mytemplate.render())

    # media
    shutil.copytree('media', os.path.join('build', 'media'))


if __name__ == '__main__':
    generate()
