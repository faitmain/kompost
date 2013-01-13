# -*- encoding: utf8 -*-
import os
import json
import socket
from ConfigParser import ConfigParser
import logging

from rst2pdf.createpdf import main as create_pdf

from kompost.util import configure_logger



COVER = """\
.

.. role:: wfont


.. header::

   .. class:: wfont

   ###Section### - FaitMain Magazine - Janvier 2013


.. footer::

   .. class:: wfont

   Page ###Page###/###Total### - © 2012 FaitMain Magazine - CC-By-NC-SA


.. raw:: pdf

   PageBreak page


"""

PAGEBRK = """

.. raw:: pdf

   PageBreak page


"""

article_header = ""


def generate(config):
    src = config['pdf_src']
    target = config['pdf_target']

    with open(config['jsonlist']) as f:
        jsonlist = json.loads(f.read())

    # creating a full rst
    rst = COVER

    for article in jsonlist['articles']:
        article = os.path.join(src, article)

        with open(article) as f:
            article = f.read()

        rst += article_header + article + PAGEBRK

    full = os.path.join(target, 'faitmain-janvier-2013.rst')

    with open(full, 'w') as f:
        f.write(rst)

    create_pdf([full, '--config',  config['pdf_conf']])


def main():
    configure_logger()
    config = ConfigParser()
    config.read('kompost.ini')
    config = dict(config.items('kompost'))
    target = config['target']
    src = config['src']
    socket.setdefaulttimeout(int(config.get('timeout', 10)))
    config['media'] = os.path.abspath(os.path.join(target, 'media'))
    config['generic'] = os.path.join(src, 'generic.mako')
    config['cats'] = os.path.join(src, 'category.mako')
    config['icons'] = ('pen.png', 'info.png', 'thumbsup.png',
                       'right.png', 'flash.png')
    config['metadata'] = os.path.join(target, 'metadata.json')
    generate(config)


if __name__ == '__main__':
    main()
