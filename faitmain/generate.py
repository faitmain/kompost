import os
import shutil
import json
import socket
import datetime
from ConfigParser import ConfigParser
from collections import defaultdict
import logging

import requests

from faitmain.generate_pdf import generate as pdf
from faitmain.generators import generators
from faitmain.generators._mako import Mako
from faitmain.index import get_index
from faitmain import logger



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

    for root, dirs, files in os.walk(src):
        for file in files:
            if file.endswith('.DS_Store'):
                continue

            ext = os.path.splitext(file)[-1]
            path = os.path.join(root, file)

            if ext in ('.mako', '.un~'):
                continue

            location = path[len(src) + 1:]
            file_target = os.path.join(target, location)
            target_dir = os.path.dirname(file_target)
            file_target_name, ext = os.path.splitext(file_target)
            url_target = file_target_name[len(target):] + '.html'

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # now calling the right generator
            if ext in match:
                match[ext](path, file_target, url_target)

            else:
                logger.info('Copying %r' % file_target)
                shutil.copyfile(path, file_target)

    # media
    media = config['media']

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

    for wanted in ('electronique', 'informatique', 'art', 'cuisine',
                   'ecologie'):
        if wanted in categories:
            continue
        categories[wanted] = []

    gen = Mako(config)

    for cat, paths in categories.items():
        logger.info('Generating category %r' % cat)
        url_target = '/%s.html' % cat
        file_target = os.path.join(target, cat + '.html')
        gen(config['cats'], file_target, url_target, paths=paths,
            title=cat.capitalize())
        sitemap.append(url_target)

    # creating sitemap
    sitemap_file = os.path.join(target, 'sitemap.json')
    logger.info('Generating sitemap at %r' % sitemap_file)
    now = datetime.datetime.now().isoformat()

    urlset = [{'loc': loc, 'lastmod': now,
               'changefreq': 'monthly',
               'priority': 0.1} for loc in sitemap]

    with open(sitemap_file, 'w') as f:
        f.write(json.dumps({'urlset': urlset}))

    # asking Trouvailles to index the web site
    logger.info('Indexing the whole website')
    url = config['search_server']
    data = {'sitemap': config['sitemap']}
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        logger.info('Indexation failed')
        logger.info(r.status_code)
        logger.info(r.content)


LOG_FMT = r"[%(levelname)s] %(message)s"
LOG_DATE_FMT = r"%Y-%m-%d %H:%M:%S"


def configure_logger(loglevel=logging.INFO, output="-"):
    logger.setLevel(loglevel)
    if output == "-":
        h = logging.StreamHandler()
    else:
        h = logging.FileHandler(output)
    fmt = logging.Formatter(LOG_FMT, LOG_DATE_FMT)
    h.setFormatter(fmt)
    logger.addHandler(h)


def main():
    configure_logger()
    config = ConfigParser()
    config.read('faitmain.ini')
    config = dict(config.items('faitmain'))
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
