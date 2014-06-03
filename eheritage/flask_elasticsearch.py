from flask import current_app
from elasticsearch import Elasticsearch
from flask import _app_ctx_stack as stack

# See https://github.com/baijum/flask-esclient/blob/master/flask_esclient.py
# https://github.com/kazoup/flask-elasticsearch/blob/master/flask_elasticsearch.py
#

class ElasticSearch(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = stack.top

    def get_es(self):
        return Elasticsearch(current_app.config['ES_HOST'])

    def search(self, query, **kwargs):
        index = current_app.config['ES_INDEX']
        return self.get_es().search(body=query, index=index, **kwargs)

    def get(self, id, **kwargs):
        index = current_app.config['ES_INDEX']
        doc_type = current_app.config['ES_DOCTYPE']
        return self.get_es().get(id=id,
                                 index=index,
                                 doc_type=doc_type,
                                 **kwargs)

    def prepare_elasticutils_query(self, query):
        host = current_app.config['ES_HOST']
        index = current_app.config['ES_INDEX']
        doctype = current_app.config['ES_DOCTYPE']
        return query.es(urls=[host]).indexes(index).doctypes(doctype)
