from flask import render_template, flash, redirect
from flask import jsonify, request, send_file, session
from flask.ext.paginate import Pagination

from eheritage import app, db
from elasticsearch import TransportError


PAGE_SIZE = 10


@app.route("/record/<id>.json")
def get_record_json(id):
    result = db.get_heritage_place(id)
    return jsonify(result['_source'])


def parse_location_filters():
    """Parse filters from HTTP query parameters

    Looks for 'keyword', 'bounds', 'lga_name' and 'suburb'.
    Returns them as a dict for parsing to get_locations()
    """
    filters = {}
    filters['keyword'] = request.args.get('keyword', '')

    if 'north' in request.args:
        filters['bounds'] = {
            "top" : request.args.get('north', ''),
            "bottom": request.args.get('south', ''),
            "left": request.args.get('west', ''),
            "right": request.args.get('east', '')
        }

    if 'lga_name' in request.args:
        filters['lga_name'] = request.args.get('lga_name', '')

    if 'suburb' in request.args:
        filters['suburb'] = request.args.get('suburb', '')

    return filters

@app.route("/locations.json")
def locations_json():
    filters = parse_location_filters()

    try:
        num_results = int(request.args.get('num_results', '1000'))
    except ValueError:
        num_results = 1000

    results = db.get_locations(num_results, **filters)
    return jsonify(results)


@app.route("/locations/suburbs")
def locations_suburbs():
    filters = parse_location_filters()
    lga_name = request.args.get('lga_name', '')
    suburbs = db.get_all_suburbs(lga_name=lga_name,
                                 keyword=filters.get('keyword'),
                                 bounds=filters.get('bounds'))
    return jsonify(suburbs)

@app.route("/locations/lgas")
def locations_lgas():
    filters = parse_location_filters()
    lgas = db.get_all_lgas(keyword=filters.get('keyword'),
                           bounds=filters.get('bounds'))
    return jsonify(lgas)

@app.route("/locations/lgas/<lga_name>")
def locations_lgas_name(lga_name):
    places = db.get_
    return jsonify(places)

@app.route("/locations/search")
def locations_search():
    if hasattr(request.args, 'lga_name'):
        lga_name = request.args.get('lga_name', '')
        db.get_locations


@app.route("/geogrid.json")
def geogrid_json():
    filters = parse_location_filters()
    results = db.get_records_geogrid(3, **filters)
    return jsonify(results)

@app.route("/api/construction_dates")
def construction_dates():
    dates = db.get_construction_dates()

    return jsonify(dates)

#####################
## FRONT END
#####################

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/record/<id>")
def get_record(id):
    result = db.get_heritage_place(id)
    return render_template("record.html",
        record_id = result['_id'],
        record = result['_source'])

@app.route("/map")
def map():
    query = prepare_keyword_search()
    num_results = query.count()

    return render_template("map.html",
        count=num_results)


@app.route("/timeline")
def timeline():
    return render_template("timeline.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/ember/")
def ember():
    return send_file("templates/ember.html")

def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    mimetype_wants = best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

    return mimetype_wants or 'json' in request.args


def prepare_keyword_search():
    search_term = request.args.get('keyword', '')
    query = db.get_elasticutils_query()
    session['search_term'] = search_term

    if search_term:
        query = query.query(_all__match_and=search_term)

    return query

@app.route("/search/")
def search():
    """Return HTML page of search results"""

    query = prepare_keyword_search()

#######
### Add Advanced Search Restrictions to Query
    adv_search = False

    advanced_search_terms = {
        'address': 'address__match_phrase',
        'creator': 'creator__match_phrase',
        'construction_from': 'construction_start__gte',
        'construction_to': 'construction_start__lte',
    }

    for request_arg, query_type in advanced_search_terms.items():
        value = request.args.get(request_arg, '')

        if value:
            query = query.query(**{query_type: value})
            adv_search = True

########
### Setup Faceting
    active_facets = {}
    # Apply Facet Filters
    facetable_fields = ['addresses.suburb', 'state', 'architects.raw',
                        'categories.group', 'categories.name']
    for facet_field in facetable_fields:
        facet_value = request.args.get(facet_field, '')
        if facet_value:
            active_facets[facet_field] = facet_value
            query = query.query(**{facet_field: facet_value})

    query = query.facet(*facetable_fields)

    try:
        page = int(request.args.get('page', 1))

        start = (page -1) * PAGE_SIZE
        to = start + PAGE_SIZE
        print "from: %s to: %s" % (start, to)

        query = query[start:to]

    except ValueError:
        page = 1

    try:
        results = query.execute()
    except TransportError:
        return render_template("results.html")

    pagination = Pagination(
        page=page,
        total=results.count,
        css_framework='bootstrap3',
        display_msg='displaying records <b>{start} - {end}</b> of <b>{total}</b>')


    if request_wants_json():
        return jsonify({
            'results': results.results,
            'count': results.count,
            'took': results.took,
            'facets': results.facets
            })
    return render_template("results.html",
        count = results.count,
        results = results.results,
        facets = results.facets,
        adv_search = adv_search,
        active_facets = active_facets,
        pagination=pagination)