#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test docopt example.

Usage:
    eheritage.py index qld <filename> [--index=<index_name>] [--dumpdir=<qld_dump>]
    eheritage.py index vic [--index=<index_name>]
    eheritage.py get_index_version
    eheritage.py create_index <index_name>
    eheritage.py delete_index <index_name>
    eheritage.py update_alias <index_name>
    eheritage.py reindex <source> <target>
    eheritage.py -h | --help
    eheritage.py --version

Options:
    -h --help   Show help message.
    --version   Show version.
"""

from docopt import docopt
import clint
import logging
from eheritage.injest import search_index
from eheritage import app


def setup_logging():
    logger = logging.getLogger("eheritage")
    logger.setLevel(logging.DEBUG)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)



if __name__ == '__main__':
    args = docopt(__doc__, version='1.0')

    setup_logging()

    with app.app_context():
        if args['create_index']:
            print search_index.create_index(args['<index_name>'])

        elif args['update_alias']:
            print search_index.update_alias(args['<index_name>'])

        elif args['delete_index']:
            print search_index.delete_index(args['<index_name>'])

        elif args['get_index_version']:
            print search_index.get_index_version()

        elif args['reindex']:
            print search_index.reindex(args['<source>'], args['<target>'])

        elif args['index']:

            if args['qld']:
                print search_index.load_qld_data(args['<filename>'], args['--dumpdir'])

            elif args['vic']:
                print search_index.stream_vic_data(args['--index'])

