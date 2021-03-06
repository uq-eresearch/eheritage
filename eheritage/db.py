from eheritage import es
from elasticutils import S

class EHeritageS(S):
    def process_query_match_and(self, key, val, action):
        return {
            'match': {
                key: {
                    'query': val,
                    'operator': 'and'
                }
            }
        }

    def process_query_multi_match(self, key, val, action):
        return {
            'multi_match': {
                'query': val['query'],
                'fields': val['fields'],
                'operator': 'and',
                'type': 'phrase'
            }
        }

    def process_filter_exists(self, key, val, action):
        return {
            'exists': {
                "field": key
            }
        }

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



def get_elasticutils_query():
    return es.prepare_elasticutils_query(EHeritageS())

def _query_field_plus_geo_bounds(field_type, field_name,
                                 max_results=5000, extra_filter=None,
                                 keyword=None, bounds=None):
    query = {
      "aggs": {
        "field_query": {
          "terms": {
            "field": field_name,
            "size": max_results
          },
          "aggs": {
            "center_lat": {
                "avg": {
                    "field": "geolocation.lat"
                }
            },
            "center_lon": {
                "avg": {
                    "field": "geolocation.lon"
                }
            },
            "north": {
              "max": {"field": "geolocation.lat"}
            },
            "south": {
              "min": {"field": "geolocation.lat"}
            },
            "east": {
              "max": {"field": "geolocation.lon"}
            },
            "west": {
              "min": {"field": "geolocation.lon"}
            }
          }
        }
      },
      "query": {
        "filtered": {
          "filter": {
            "and": [
            {
                "exists": {"field": "geolocation"}
            }]
          }
        }
      },
      "size": 0
    }

    if bounds:
        query['query']['filtered']['filter']['and'].append({
                "geo_bounding_box" : {
                    "geolocation" : bounds
                }
            })

    if extra_filter:
        query['query']['filtered']['filter']['and'].append(extra_filter)

    if keyword:
        query['query']['filtered']['query'] = {
            'match': {
                '_all': keyword
            }
        }


    results = es.search(query)

    places = {
        field_type: [{
            "name": p['key'],
            "record_count": p['doc_count'],
            "weighted_center": {
                "lat": p['center_lat']['value'],
                "lon": p['center_lon']['value']
            },
            "bounds": {
                "n": p['north']['value'],
                "s": p['south']['value'],
                "e": p['east']['value'],
                "w": p['west']['value']
            }
        } for p in results['aggregations']['field_query']['buckets']]
    }
    return places

def get_all_lgas(keyword=None, bounds=None):
    """Return details of all Local Government Area

    Includes name, geographic centre, bounds and number of contained records
    """
    return _query_field_plus_geo_bounds("lgas", "addresses.lga_name",
                keyword=keyword, bounds=bounds)

def get_all_suburbs(lga_name, keyword=None, bounds=None):
    """Return details of all Suburbs

    Includes name, geographic centre, bounds and number of contained records
    """
    extra_filter = {}
    if lga_name:
        extra_filter['term'] = {
                'addresses.lga_name': lga_name
            }

    return _query_field_plus_geo_bounds("suburbs", "addresses.suburb",
        extra_filter=extra_filter, keyword=keyword, bounds=bounds)


def get_locations(num_results=1000, keyword=None, bounds=None,
                  lga_name=None, suburb=None):
    """Return a set of locations matching the arguments
    """
    query = {
        "size": num_results,
        "fields": ("geolocation.lat", "geolocation.lon", "name"),
        "filter": {
            "and": [
                {
                    "exists": {"field": "geolocation"}
                }
            ]
        }
    }
    if keyword:
        query['query'] = {
            "match": {
                "_all": keyword
            }
        }
    if bounds:
        query['filter']['and'].append({
                "geo_bounding_box" : {
                    "geolocation" : bounds
                }
            })
    if lga_name:
        query['filter']['and'].append({
                "term": {
                    "addresses.lga_name": lga_name
                }
            })
    if suburb:
        query['filter']['and'].append({
                "term": {
                    "addresses.suburb": suburb
                }
            })

    return es.search(query)


def get_heritage_place(id):
    """Retrieve a single heritage place
    """
    return es.get(id)


def get_records_geogrid(precision, keyword=None, bounds=None):
    """Return geohash grids containing records
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

    return es.search(query)


def get_construction_dates():
    """Return summary information of construction start and end dates
    """
    query = {
      "aggs" : {
        "construction_years" : {
          "terms" : {
            "field" : "construction_start",
            "order" : { "_term" : "asc" },
            "size": 250
          }
        },
        "num_construction_years" : {
          "cardinality" : {
            "field" : "construction_start"
          }
        },
        "construction_decades": {
          "histogram": {
            "field" : "construction_start",
            "interval": 10
          }
        },
        "construction_end_decades": {
          "histogram": {
            "field" : "construction_end",
            "interval": 10
          }
        }
      },
      "size": 0
    }

    return es.search(query)


def get_field_values(field, num_results=5000):
    query = {
      "aggs": {
        "field_values": { # Defined name
          "terms": {
            "field": field,
            "size": num_results
          }
        }
      },
      "filter": {
    # //    "term": {
    # //      "addresses.lga_name": "YARRA CITY"  
    # //    }
      },
      "size": 0
    }

    es_results = es.search(query)
    results = [{"val": bucket['key'], "num": bucket['doc_count']}
        for bucket in es_results['aggregations']['field_values']['buckets'] ]

    return results