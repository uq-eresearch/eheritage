from eheritage import es



def _query_field_plus_geo_bounds(field_type, field_name, max_results=1000):
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
      "size": 0
    }

    results = es.search(query)

    places = {
        field_type: [{
            "name": p['key'],
            "count": p['doc_count'],
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

def get_all_lgas():
    return _query_field_plus_geo_bounds("lgas", "addresses.lga_name")

def get_all_suburbs():
    return _query_field_plus_geo_bounds("suburbs", "addresses.suburb")


def get_locations(extra_query={}, num_results=1000):
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
    if extra_query:
        if 'match' in extra_query:
            query['query'] = {"match": extra_query["match"] }
        if 'filter' in extra_query:
            query['filter']['and'].append(extra_query["filter"])

    return es.search(query)


def get_heritage_place(id):
    """Retrieve a single heritage place
    """
    return es.get(id)


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

    return es.search(query)


def get_construction_dates():
    """Return the results of a histogram query on construction start dates
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