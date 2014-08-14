from flask import Flask
from eheritage.utils import IterableAwareEncoder
from flask.ext.assets import Environment, Bundle
from eheritage.flask_elasticsearch import ElasticSearch
import os

app = Flask(__name__)


app.config.from_object('eheritage.default_settings')
app.config.from_envvar('EHERITAGE_SETTINGS', silent=True)


###
# Initialise ElasticSearch
###

es = ElasticSearch(app)



### Setup Logging
# if not app.debug:
import logging
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

loggers = [app.logger, logging.getLogger('elasticsearch')]
for logger in loggers:
    logger.setLevel(logging.WARNING)
    logger.addHandler(stream_handler)



# When I'm ready to fix this with bower and stuff
# look at http://adambard.com/blog/fresh-flask-setup/

environment = Environment(app)
js = Bundle('app.js',
    filters='jsmin', output='gen/packed.js')
environment.register('js_all', js)

scss = Bundle('*.scss', filters='scss', output='gen/scss.css')
css = Bundle('style.css', scss,
    filters='pyscss,cssmin', output='gen/all.css')

app.json_encoder = IterableAwareEncoder


# Absolute filesystem path to the secret file which holds this project's
# SECRET_KEY. Will be auto-generated the first time this file is interpreted.
# SECRET_FILE = os.path.normpath(os.path.join(DJANGO_ROOT, 'deploy', 'SECRET'))
SECRET_FILE = 'SECRET'

########## KEY CONFIGURATION
# Try to load the SECRET_KEY from our SECRET_FILE. If that fails, then generate
# a random SECRET_KEY and save it into our SECRET_FILE for future loading. If
# everything fails, then just raise an exception.
try:
    app.secret_key = open(SECRET_FILE).read().strip()
except IOError:
    try:
        app.secret_key = os.urandom(24)
        with open(SECRET_FILE, 'w') as f:
            f.write(app.secret_key)
    except IOError:
        raise Exception('Cannot open file `%s` for writing.' % SECRET_FILE)
########## END KEY CONFIGURATION



from eheritage import template_extensions
from eheritage import views
from eheritage import error_handlers