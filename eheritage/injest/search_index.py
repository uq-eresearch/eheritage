# -*- coding: utf-8 -*-

"""
This module contains the code for putting heritage places into a search index.

"""

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError


ES_HOST = "192.168.10.200"
ES_INDEX = "eheritage"
ES_ALIAS = "eheritage"
ES_DOCTYPE = "heritage_place"
es = Elasticsearch(ES_HOST)

from elasticutils import get_es, S

def get_elasticutils_query():
    return S().es(urls=[ES_HOST]).indexes(ES_INDEX).doctypes(ES_DOCTYPE)



class GeoS(S):
    def process_filter_geoboundingbox(self, key, val, action):
        """
        http://elasticutils.readthedocs.org/en/latest/api.html#elasticutils.S
        See http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-geo-bounding-box-filter.html
        """
        top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon = val
        geofilter = {
            'geo_bounding_box': {
                key: {
                    "top_left" : {
                        "lat" : top_left_lat,
                        "lon" : top_left_lon
                    },
                    "bottom_right" : {
                        "lat" : bottom_right_lat,
                        "lon" : bottom_right_lon
                    }

                }
            }
        }
        return geofilter

        #return {'funkyfilter': {'field': key, 'value': val}}



def create_index():
    body = {
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
                        "index": "not_analyzed"
                    },
                    "architects": {
                        "type": "string",
                        "index": "not_analyzed"
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
    return es.indices.create(ES_INDEX, body)


def add_heritage_place(place):
    """Add a heritage place to the search index

    :param place: Dictionary defining a heritage place.
    """
    try:
        id = "%s-%s" % (place['state'], place['id'])
        result = es.index(index=ES_INDEX, doc_type=ES_DOCTYPE, id=id, body=place)
        # print result
    except AttributeError as e:
        print e
        print place
        return False

    return True


def simple_search(keyword_term, page=1, other_fields={}):
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
    res = es.search(index=ES_INDEX, body=query)

    return res

def advanced_search(search_terms, page=1):
    """
    search_terms: a dictionary of search terms
    """
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
    res = es.search(index=ES_INDEX, body=query)

    return res



def get_heritage_place(id):
    """Retrieve a single heritage place
    """
    res = es.get(index=ES_INDEX, doc_type=ES_DOCTYPE, id=id)
    return res


def get_locations(extra_query={}):
    query = {
        "size": 10000,
        "fields": ("geolocation.lat", "geolocation.lon", "name"),
        "filter": {
            "exists": {"field": "geolocation"}
        }
    }
    if extra_query:
        query['query'] = extra_query
    res = es.search(index=ES_INDEX, doc_type=ES_DOCTYPE, body=query)

    return res

def get_geogrid(precision, extra_query={}):
    """
    """
    query = {
        "aggregations" : {
            "geogrid" : {
                "geohash_grid" : {
                    "field" : "geolocation",
                    "precision" : precision
                }
            }
        }
    }
    if extra_query:
        query['query'] = extra_query
    res = es.search(index=ES_INDEX, doc_type=ES_DOCTYPE, body=query)

    return res


def delete_index():
    """Delete the entire index of heritage places
    DANGER!!
    """
    return es.indices.delete(ES_INDEX)

from clint.textui import progress
import json
import traceback

def load_qld_data():
    from qld import parse_ahpi_xml

    qld_filename = "/mnt/groups/maenad/activities/e-Heritage/QLD/heritage_list.xml"

    qld_places = parse_ahpi_xml(qld_filename)

    for place in progress.dots(qld_places):
        add_heritage_place(place)


def make_es_index_obj(docs):
    """Generator function that turns ES _source documents into
    index documents suitable for streaming_bulk"""

    for doc in docs:
        insert_doc = {
            '_index': ES_INDEX,
            '_type': ES_DOCTYPE,
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


from elasticsearch.helpers import streaming_bulk
def stream_vic_data():
    import vic

    num = vic.get_number_of_places()
    print "Importing %d Victorian Heritage Places" % num

    for ok, result in progress.bar(streaming_bulk(es, 
        make_es_index_obj(vic.all_places())), width=80, expected_size=num):
        if not ok:
            action, result = result.popitem()
            doc_id = '/%s/commits/%s' % (index, result['_id'])
            print('Failed to %s document %s: %r' % (action, doc_id, result))