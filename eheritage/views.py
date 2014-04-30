from flask import render_template, flash, redirect
from flask import jsonify, request, send_file
from flask.ext.paginate import Pagination

from injest.search_index import simple_search, get_heritage_place, get_all_locations
from injest.search_index import get_elasticutils_query, get_geogrid
from eheritage import app
from forms import SearchForm

def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

@app.route("/")
def index():
    form = SearchForm()
    return render_template("index.html",
        form = form)

@app.route("/ember/")
def ember():
    return send_file("templates/ember.html")
PAGE_SIZE = 10

@app.route("/search/")
def search(search_term=None):
    search_term = request.args.get('keyword', '')
    address_term = request.args.get('address', '')

    query = get_elasticutils_query()


    if search_term:
        query = query.query(_all=search_term)
    if address_term:
        query = query.query(**{'addresses.lga_name': address_term})


    try:
        page = int(request.args.get('page', 1))

        start = (page -1) * PAGE_SIZE
        to = start + PAGE_SIZE
        print "from: %s to: %s" % (start, to)

        query = query[start:to]

    except ValueError:
        page = 1

    results = query.execute()

    pagination = Pagination(page=page, total=results.count, css_framework='bootstrap3')

    if request_wants_json():
        # return jsonify(items=[x.to_json() for x in items])
        # import ipdb; ipdb.set_trace()
        return jsonify({
            'results': results.results,
            'count': results.count,
            'took': results.took
            })
    return render_template("results.html",
        results = results.results,
        search_term = search_term,
        address_term = address_term,
        pagination=pagination)


@app.route("/record/<id>")
def get_record(id):
    result = get_heritage_place(id)
    return jsonify(result['_source'])

@app.route("/search/<search_term>.json")
def search_json(search_term):
    results = simple_search(search_term)
    return jsonify(simple_search(search_term)['hits'])

@app.route("/locations.json")
def locations_json():
    results = get_all_locations()
    return jsonify(results)

@app.route("/geogrid.json")
def geogrid_json():
    results = get_geogrid(3)
    return jsonify(results)

@app.route("/map")
def map():
    return render_template("map.html")



if __name__ == "__main__":
    app.debug = True
    app.run()