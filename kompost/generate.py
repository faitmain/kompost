import os
import shutil
import json
import socket
import datetime
from collections import defaultdict
import tempfile
import codecs
import sys

import requests
from konfig import Config

from feedgenerator import Atom1Feed

from kompost.generate_pdf import generate as pdf
from kompost.generators import generators
from kompost.generators._mako import Mako
from kompost.generators.rst import RestructuredText
from kompost.index import get_index, get_articles
from kompost import logger
from kompost.util import configure_logger, str2authorid


AUTHOR_ARTICLES = u"""\

Articles:

%s

"""


def generate(config):
    sitemap = []
    target = config['target']
    src = config['src']

    if not os.path.exists(target):
        os.mkdir(target)

    gens = [klass(config) for klass in generators]
    match = {}

    for gen in gens:
        for ext in gen.exts:
            match[ext] = gen

    cats = config.get('categories', '').split(',')
    cats = [cat.strip() for cat in cats if cat.strip() != '']
    config['categories'] = cats

    for path in ('cnd', 'siteurl'):
        if os.path.exists(config[path]):
            config[path] = os.path.abspath(config[path])

    source_root = config.get('source_root')

    for root, dirs, files in os.walk(src):
        for file in files:
            if file.startswith('_'):
                continue

            if file.endswith('.DS_Store'):
                continue

            ext = os.path.splitext(file)[-1]
            path = os.path.join(root, file)

            if ext in ('.mako', '.un~'):
                continue

            # configurable XXX
            if (os.path.split(path)[0] == 'src/auteurs' and
                file.endswith('.rst')):
                continue

            location = path[len(src) + 1:]
            file_target = os.path.join(target, location)
            target_dir = os.path.dirname(file_target)
            file_target_name, ext = os.path.splitext(file_target)
            url_target = file_target_name[len(target):] + '.html'

            if source_root is not None:
                config['github'] = os.path.join(source_root, location)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # now calling the right generator
            if ext in match:
                try:
                    match[ext](path, file_target, url_target, config=config)
                except Exception:
                    logger.info('Failed on %s' % path)
                    raise
                sitemap.append((url_target, True))
            else:
                logger.info('Copying %r' % file_target)
                shutil.copyfile(path, file_target)

    if 'github' in config:
        del config['github']

    # media
    media = str(config['media'])

    if os.path.exists(media):
        shutil.rmtree(media)

    shutil.copytree('media', media)

    # building category pages now
    categories = defaultdict(list)

    for key, index in get_index():
        path, title = key.split(':')

        for key, value in index.items():
            if key != 'category':
                continue
            for cat in value:
                categories[cat].append((path, title))

    for wanted in config['categories']:
        if wanted in categories:
            continue
        categories[wanted] = []

    gen = Mako(config)

    for cat, paths in categories.items():
        logger.info('Generating category %r' % cat)
        url_target = '/%s.html' % cat
        file_target = os.path.join(target, cat + '.html')
        gen(config['cats'], file_target, url_target, paths=paths,
            title=cat.capitalize(), config=config,
            category=cat)
        sitemap.append((url_target, False))

    # creating the authors index page
    authors = {}
    for key, index in get_index():
        path, title = key.split(':')
        for key, authors_ in index.items():
            if key != 'author':
                continue

            for author_name in authors_:
                author_id = str2authorid(author_name)
                if author_id in authors:
                    authors[author_id]['articles'].append((title, path))
                else:
                    # should be configurable
                    link = '%s/auteurs/%s.html' % (config['siteurl'], author_id)
                    authors[author_id] = {'link': link,
                                          'articles': [(title, path)],
                                          'name': author_name}

    authors = authors.items()
    authors.sort()

    # XXX should be configurable...
    authors_template = os.path.join(src, 'auteurs', 'index.mako')
    logger.info('Generating authors index')
    url_target = '/auteurs/index.html'
    file_target = os.path.join(target, 'auteurs', 'index.html')
    gen(authors_template, file_target, url_target, authors=authors,
        title="Auteurs", config=config)
    sitemap.append((url_target, False))

    # creating the author pages
    gen = RestructuredText(config)
    for author_id, data in authors:
        template = os.path.join(src, 'auteurs', '%s.rst' % author_id)
        if not os.path.exists(template):
            logger.warning('Template not found for author %r' % author_id)
            continue

        # we're supposed to find an author .rst file in /auteur
        url_target = '/auteurs/%s.html' % author_id
        file_target = os.path.join(target, 'auteurs', '%s.html' % author_id)

        fd, tmp = tempfile.mkstemp()
        os.close(fd)

        def _line(line):
            title, path = line
            path = '%s/%s' % (config['siteurl'].rstrip('/'), path)
            return u'- `%s <%s>`_' % (title, path)

        articles = AUTHOR_ARTICLES % '\n'.join([_line(data) for data in
                                                data['articles']])

        with codecs.open(template, encoding='utf8') as source_file:
            with codecs.open(tmp, 'w', encoding='utf8') as target_file:
                data = source_file.read()
                data += articles + '\n'
                target_file.write(data)

        try:
            gen(tmp, file_target, url_target, config=config)
        finally:
            os.remove(tmp)

        sitemap.append((url_target, True))

    # create the atom feed
    siteurl = config.get('siteurl')
    feed = Atom1Feed(
        title='FaitMain.org',
        link=siteurl,
        feed_url=siteurl + 'feed.xml',
        description=config.get('site-description'))

    for key, article in get_articles():
        path, title = key.split(':')

        feed.add_item(
            title=title,
            link='%s/%s' % (siteurl, path),
            description=article['body'],
            categories=article['category'],
            author_name=article['author'],
            pubdate=article['date'])

    with open(os.path.join(target, 'feed.xml'), 'w') as f:
        feed.write(f, 'utf-8')

    # creating sitemap
    sitemap_file = os.path.join(target, 'sitemap.json')
    logger.info('Generating sitemap at %r' % sitemap_file)
    now = datetime.datetime.now().isoformat()

    urlset = [{'loc': loc, 'lastmod': now,
               'changefreq': 'monthly',
               'priority': 0.1,
               'indexable': int(indexable)}
               for loc, indexable in sitemap]

    with open(sitemap_file, 'w') as f:
        f.write(json.dumps({'urlset': urlset}))

    # asking Trouvailles to index the web site
    if int(config['indexing']) == 0:
        return

    logger.info('Indexing the whole website')
    url = config['search_server']
    data = {'sitemap': config['sitemap']}
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        logger.info('Indexation failed')
        logger.info(r.status_code)
        logger.info(r.content)


def main():
    configure_logger()
    if len(sys.argv) > 1:
        ini = sys.argv[1]
    else:
        ini = "kompost.ini"
    os.environ['CURDIR'] = os.getcwd()
    config = Config(codecs.open(ini, "r", "utf8"))
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
    pdf(config)


if __name__ == '__main__':
    main()
