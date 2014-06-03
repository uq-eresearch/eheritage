# -*- coding: utf-8 -*-

"""
This module contains the code for putting heritage places into a search index.

"""

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
import elasticsearch.helpers
from clint.textui import progress
import json
import traceback
from flask import current_app

from flask import g


def get_es():
    es = getattr(g, '_es', None)
    if es is None:
        ES_HOST = current_app.config['ES_HOST']
        ES_INDEX = current_app.config['ES_INDEX']
        ES_ALIAS = current_app.config['ES_ALIAS']
        ES_DOCTYPE = current_app.config['ES_DOCTYPE']
        es = g._es = Elasticsearch(ES_HOST)
    return es




def reindex(source, target):
    """ReIndex data from source into target

    Used when a new mapping has been created
    """
    es = get_es()
    elasticsearch.helpers.reindex(es, source, target)


def create_index(index_name):
    if not index_name:
        index_name = current_app.config['ES_INDEX']
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
    return get_es().indices.create(index_name, mapping_body)


def add_heritage_place(place):
    """Add a heritage place to the search index

    :param place: Dictionary defining a heritage place.
    """

    ES_INDEX = current_app.config['ES_INDEX']
    ES_DOCTYPE = current_app.config['ES_DOCTYPE']
    try:
        id = "%s-%s" % (place['state'], place['id'])
        result = get_es().index(index=ES_INDEX, doc_type=ES_DOCTYPE, id=id, body=place)
        # print result
    except AttributeError as e:
        print e
        print place
        return False

    return True


def simple_search(keyword_term, page=1, other_fields={}):
    ES_INDEX = current_app.config['ES_INDEX']

    es_size = 10
    es_from = (page-1) * es_size
    matches = {
        "_all": keyword_term
    }
    matches.update()
    query = {
        "from": es_from,
        "size": es_size,
        "query": {
            "match": {
                "_all": keyword_term
            }
        },
        "facets" : {
            "state" : { "terms" : {"field" : "state"} }
        },
    }
    res = get_es().search(index=ES_INDEX, body=query)

    return res

def advanced_search(search_terms, page=1):
    """
    search_terms: a dictionary of search terms
    """
    ES_INDEX = current_app.config['ES_INDEX']

    es_size = 10
    es_from = (page-1) * es_size
    query = {
        "from": es_from,
        "size": es_size,
        "query": {
            "match": {
                search_terms
            }
        },
        "facets" : {
            "state" : { "terms" : {"field" : "state"} }
        },
    }
    results = get_es().search(index=ES_INDEX, body=query)

    return results


def delete_index(index_name):
    """Delete the entire index of heritage places - DANGER!!
    """
    if not index_name:
        index_name = current_app.config['ES_INDEX']

    return get_es().indices.delete(index_name)


def load_qld_data(qld_filename):
    from qld import parse_ahpi_xml

    qld_places = parse_ahpi_xml(qld_filename)

    for place in progress.dots(qld_places):
        add_heritage_place(place)


def make_es_index_obj(docs, es_index, es_doctype):
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
    import vic

    num = vic.get_number_of_places()
    print "Importing %d Victorian Heritage Places" % num

    for place in progress.bar(vic.all_places(), width=80, expected_size=num):
        try:
            add_heritage_place(place)
        except RequestError, err:
            print json.dumps(place, indent=2)
            print traceback.format_exc()

            raise RequestError


def stream_vic_data():
    import vic
    ES_INDEX = current_app.config['ES_INDEX']
    ES_DOCTYPE = current_app.config['ES_DOCTYPE']

    num = vic.get_number_of_places()
    print "Importing %d Victorian Heritage Places" % num

    es = get_es()

    for ok, result in progress.bar(
                elasticsearch.helpers.streaming_bulk(
                            es,
                            make_es_index_obj(vic.all_places(), ES_INDEX, ES_DOCTYPE)
                      ), width=80, expected_size=num):
        if not ok:
            action, result = result.popitem()
            doc_id = '/%s/commits/%s' % (ES_INDEX, result['_id'])
            print('Failed to %s document %s: %r' % (action, doc_id, result))