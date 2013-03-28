# -*- encoding: utf8 -*-
import os
import json
import socket
from ConfigParser import ConfigParser
import logging
import codecs

from rst2pdf.createpdf import main as create_pdf

from kompost.util import configure_logger



COVER = """\
.

.. role:: wfont

.. role:: rightfloat

.. role:: leftfloat


.. header::

   .. class:: wfont

   %s


.. footer::

   .. class:: wfont

   %s


.. raw:: pdf

   PageBreak page


"""

PAGEBRK = """

.. raw:: pdf

   PageBreak page


"""

article_header = ""

_FOOTER = """

.. |pen| image:: ../media/pen.png
.. |info| image:: ../media/info.png
.. |thumbsup| image:: ../media/thumbsup.png
.. |right| image:: ../media/right.png
.. |flash| image:: ../media/flash.png
.. |infosign| image:: icon-info-sign
"""



def generate(config):
    src = config['pdf_src']
    target = config['pdf_target']
    name = config['pdf_name']

    with open(config['jsonlist']) as f:
        jsonlist = json.loads(f.read())

    # creating a full rst
    rst = COVER % (config['pdf_header'], config['pdf_footer'])

    for article in jsonlist['articles']:
        article = os.path.join(src, article)

        with codecs.open(article, "r", "utf8") as f:
            article = f.read()

        rst += article_header + article + PAGEBRK

    rst += _FOOTER
    full = os.path.join(target, '%s.rst' % name)
    rst = rst.replace(u'\xa0', u' ')

    with codecs.open(full, 'w', 'utf8') as f:
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
