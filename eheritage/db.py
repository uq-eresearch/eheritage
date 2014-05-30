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
    """Return details of all Local Government Area

    Includes name, geographic centre, bounds and number of contained records
    """
    return _query_field_plus_geo_bounds("lgas", "addresses.lga_name")

def get_all_suburbs():
    """Return details of all Suburbs

    Includes name, geographic centre, bounds and number of contained records
    """
    return _query_field_plus_geo_bounds("suburbs", "addresses.suburb")


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