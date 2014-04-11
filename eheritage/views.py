from flask import render_template, flash, redirect
from eheritage import app

from forms import SearchForm

@app.route("/")
def index():
    form = SearchForm()
    return render_template("index.html",
        form = form)


from injest.search_index import keyword_search, get_heritage_place, get_all_locations
from flask import jsonify, request
from flask.ext.paginate import Pagination

@app.route("/search/")
# @app.route("/search/<search_term>")
def search(search_term=None):
    search_term = request.args.get('keyword', '')

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1


    if search_term:
        results = keyword_search(search_term, page)
    else:
        results = None

    pagination = Pagination(page=page, total=results['hits']['total'], css_framework='bootstrap3')

    return render_template("results.html",
        results = results['hits'],
        search_term = search_term,
        pagination=pagination)


@app.route("/record/<id>")
def get_record(id):
    result = get_heritage_place(id)
    return jsonify(result['_source'])

@app.route("/search/<search_term>.json")
def search_json(search_term):
    results = keyword_search(search_term)
    return jsonify(keyword_search(search_term)['hits'])

@app.route("/locations.json")
def locations_json():
    results = get_all_locations()
    return jsonify(results)

@app.route("/map")
def map():
    return render_template("map.html")



if __name__ == "__main__":
    app.debug = True
    app.run()