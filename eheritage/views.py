from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"


from injest.search_index import keyword_search
from flask import jsonify

@app.route("/search/<search_term>")
def search(search_term):
    return str(keyword_search(search_term)['hits'])


if __name__ == "__main__":
    app.debug = True
    app.run()