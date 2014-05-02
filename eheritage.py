#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
"""Test docopt example.
 
Usage:
    eheritage.py index (vic|qld)
    eheritage.py get_index_version
    eheritage.py create_index
    eheritage.py delete_index
    eheritage.py reindex <old_version> <new_version>
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
            print search_index.create_index()

        elif args['delete_index']:
            print search_index.delete_index()

        elif args['get_index_version']:
            print 'Not Implemented!'

        elif args['index']:

            if args['qld']:
                print search_index.load_qld_data()

            elif args['vic']:
                print search_index.stream_vic_data()

