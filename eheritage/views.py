from flask import render_template, flash, redirect
from flask import jsonify, request, send_file, session
from flask.ext.paginate import Pagination
from flask import current_app

from injest.search_index import simple_search, get_heritage_place, get_locations
from injest.search_index import get_elasticutils_query, get_geogrid
from eheritage import app
from elasticsearch import TransportError

def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    mimetype_wants = best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

    return mimetype_wants or 'json' in request.args


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/ember/")
def ember():
    return send_file("templates/ember.html")
PAGE_SIZE = 10

def prepare_keyword_search():
    search_term = request.args.get('keyword', '')
    query = get_elasticutils_query()
    session['search_term'] = search_term

    if search_term:
        query = query.query(_all__match_and=search_term)

    return query

@app.route("/search/")
def search():

    query = prepare_keyword_search()

    adv_search = False

    address_term = request.args.get('address', '')
    creator_term = request.args.get('creator', '')

    if address_term:
        query = query.query(**{'address__match_phrase': address_term})
        adv_search = True
    if creator_term:
        query = query.query(**{'architects__match': creator_term})
        adv_search = True

    query = query.facet('state', 'addresses.lga_name', 'addresses.suburb', 'architects.raw')

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
        # return jsonify(items=[x.to_json() for x in items])
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
        pagination=pagination)


@app.route("/record/<id>")
def get_record(id):
    result = get_heritage_place(id)
    return render_template("record.html",
        record = result['_source'])

@app.route("/record/<id>.json")
def get_record_json(id):
    result = get_heritage_place(id)
    return jsonify(result['_source'])

@app.route("/search/<search_term>.json")
def search_json(search_term):
    results = simple_search(search_term)
    return jsonify(simple_search(search_term)['hits'])


def generate_location_query():
    search_term = request.args.get('keyword', '')
    if search_term:
        return {
            "match": {
                "_all": search_term
            }
        }
    else:
        return None

@app.route("/locations.json")
def locations_json():
    query = generate_location_query()
    results = get_locations(query)
    return jsonify(results)

@app.route("/geogrid.json")
def geogrid_json():
    query = generate_location_query()
    results = get_geogrid(3, query)
    return jsonify(results)

@app.route("/map")
def map():
    query = prepare_keyword_search()
    num_results = query.count()

    return render_template("map.html",
        count=num_results)