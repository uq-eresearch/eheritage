# -*- coding: utf-8 -*-
"""
This module contains the code for importing heritage places into a search index

"""
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
import elasticsearch.helpers
from clint.textui import progress
import json
import traceback
from flask import current_app
from eheritage import es

from flask import g
import vic

def reindex(source, target):
    """ReIndex data from source into target

    Used when a new mapping has been created
    """
    return elasticsearch.helpers.reindex(es.get_es(), source, target)


def create_index(index_name):
    mapping_body = {
        "mappings": {
            "heritage_place": {
                "_source": {
                    "enabled": True
                },
                "_all": {
                    "enabled": True
                },
                "properties": {
                    "architectural_styles": {
                        "type": "string",
                        "fields" : {
                          "raw" : {"type" : "string", "index" : "not_analyzed"}
                        }
                    },
                    "architects": {
                        "type": "string",
                        "fields" : {
                          "raw" : {"type" : "string", "index" : "not_analyzed"}
                        }
                    },
                    "categories": {
                        "type": "object",
                        "properties": {
                            "name": {"type" : "string", "index" : "not_analyzed"},
                            "group": {"type" : "string", "index" : "not_analyzed"}
                        }
                    },
                    "date_created": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "date_modified": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "lga": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "place_details_url": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "url": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "vhr_number": {
                        "type": "string"
                    },
                    "status_name": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "geolocation": {
                        "type": "geo_point",
                        "lat_lon": True,
                        "geohash": True
                    },
                    "address": { "type": "string" },
                    "addresses": {
                        "type": "object",
                        "properties": {
                            "street_number": { "type": "string", "copy_to": "address" },
                            "address": { "type": "string", "copy_to": "address" },
                            "street_name": { "type": "string", "copy_to": "address" },
                            "suburb": { "type": "string", "index": "not_analyzed", "copy_to": "address" },
                            "state": { "type": "string", "copy_to": "address" },
                            "country": { "type": "string", "copy_to": "address" },
                            "postcode": { "type": "string", "copy_to": "address" },
                            "lga_name": { "type": "string", "index": "not_analyzed", "copy_to": "address" },
                        }

                    }

                }
            }
        }
    }
    connection = es.get_es()
    return connection.indices.create(index_name, mapping_body)


def add_heritage_place(place):
    """Add a heritage place to the search index

    :param place: Dictionary defining a heritage place.
    """

    ES_INDEX = current_app.config['ES_INDEX']
    ES_DOCTYPE = current_app.config['ES_DOCTYPE']
    try:
        id = "%s-%s" % (place['state'], place['id'])
        connection = es.get_es()
        result = connection.index(index=ES_INDEX, doc_type=ES_DOCTYPE,
            id=id, body=place)
        # print result
    except AttributeError as e:
        print e
        print place
        return False

    return True


def update_alias(index_name):
    connection = es.get_es()
    alias_name = current_app.config['ES_ALIAS']
    print connection.indices.delete_alias(name=alias_name, index="_all")
    return connection.indices.put_alias(index=index_name, name=alias_name)

def delete_index(index_name):
    """Delete the entire index of heritage places - DANGER!!
    """
    connection = es.get_es()

    return connection.indices.delete(index_name)


def get_index_version():
    index_name = current_app.config['ES_INDEX']

    connection = es.get_es()
    return connection.indices.get_alias(index_name)

import qld_ehp_site_parser

def load_qld_data(qld_filename, dumpdir=None):
    from qld import parse_ahpi_xml

    qld_places = parse_ahpi_xml(qld_filename)

    for place in progress.dots(qld_places):
        if dumpdir:
            extra = qld_ehp_site_parser.load_extra(place['url'], dumpdir)
            place.update(extra)
        add_heritage_place(place)


def indexable_objects_iter(docs, es_index, es_doctype):
    """Generator function that turns ES _source documents into
    index documents suitable for streaming_bulk"""

    for doc in docs:
        insert_doc = {
            '_index': es_index,
            '_type': es_doctype,
            '_id': "%s-%s" % (doc['state'], doc['id']),
            '_source': doc
        }
        yield insert_doc


def load_vic_data():

    num = vic.get_number_of_places()
    print "Importing %d Victorian Heritage Places" % num

    for place in progress.bar(vic.all_places(), width=80, expected_size=num):
        try:
            add_heritage_place(place)
        except RequestError, err:
            print json.dumps(place, indent=2)
            print traceback.format_exc()

            raise RequestError


def stream_vic_data(index_name=None):
    if not index_name:
        index_name = current_app.config['ES_INDEX']
    ES_DOCTYPE = current_app.config['ES_DOCTYPE']

    num = vic.get_number_of_places()
    print "Importing %d Victorian Heritage Places" % num

    for ok, result in progress.bar(
                        elasticsearch.helpers.streaming_bulk(es.get_es(),
                            indexable_objects_iter(vic.all_places(),
                                index_name, ES_DOCTYPE
                            ), chunk_size=100
                      ), width=80, expected_size=num):
        index = result.get('index', {})
        status = index.get('status')
        if not ok and status != 200:
            action, result = result.popitem()
            doc_id = '/%s/commits/%s' % (index_name, result['_id'])
            print('Failed to %s document %s: %r' % (action, doc_id, result))