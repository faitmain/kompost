import codecs
import os

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import RichTraceback

from kompost import logger


class Mako(object):

    exts = ('.html',)

    def __init__(self, config):
        self.config = config
        self.lookup = TemplateLookup(directories=['.'])

    def __call__(self, path, target, url_target, **options):
        target = os.path.splitext(target)[0] + '.html'
        mytemplate = Template(filename=path, lookup=self.lookup)
        logger.info('Generating %r' % target)

        with codecs.open(target, 'w', encoding='utf8') as f:
            try:
                f.write(mytemplate.render(**options))
            except Exception:
                traceback = RichTraceback()
                for filename, lineno, function, line in traceback.traceback:
                    print "File %s, line %s, in %s" % (filename,
                                                       lineno, function)
                    print line, "\n"
                raise
