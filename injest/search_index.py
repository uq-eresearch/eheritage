# -*- coding: utf-8 -*-

"""
This module contains the code for putting heritage places into a search index.

"""

from elasticsearch import Elasticsearch

ES_HOST = "192.168.10.200"
ES_INDEX = "eheritage"
ES_DOCTYPE = "heritage_place"
es = Elasticsearch(ES_HOST)


def add_heritage_place(place):
    """Add a heritage place to the search index

    :param place: Dictionary defining a heritage place.
    """
    try:
        id = "%s-%s" % (place['state'], place['id'])
        result = es.index(index=ES_INDEX, doc_type=ES_DOCTYPE, id=id, body=place)
        print result
    except AttributeError as e:
        print e
        print place
        return False

    return True


def keyword_search(search_term):
    res = es.search(index=ES_INDEX, body={"query": {"match": {"_all": search_term}}})

    return res


if __name__ == "__main__":
    from qld import parse_ahpi_xml

    hp_filename = "/mnt/groups/maenad/activities/e-Heritage/QLD/heritage_list.xml"

    result = parse_ahpi_xml(hp_filename, add_heritage_place)

    print result