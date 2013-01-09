# -*- encoding: utf8 -*-
import os
from rst2pdf.createpdf import main
import json


COVER = """\
Magazine FaitMain
=================

**Janvier 2013**

.. note::

   PDF généré automatiquement avec le contenu du numéro de Janvier.

**Bonne Lecture!**


.. header::

   FaitMain - Janvier 2013


.. footer::

   Page ###Page### / ###Total### - © 2012 FaitMain - CC-By-NC-SA


.. raw:: pdf

   OddPageBreak

"""

PAGEBRK = """

.. raw:: pdf

   OddPageBreak

"""

article_header = """

.. header::

   What the feuille - FaitMain - Janvier 2013

"""


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

    main([full, '--config', 'pdf.conf'])


if __name__ == '__main__':
    generate()
