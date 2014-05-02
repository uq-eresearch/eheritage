from flask import Flask
from eheritage.utils import IterableAwareEncoder
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)


app.config.from_object('eheritage.default_settings')
app.config.from_envvar('EHERITAGE_SETTINGS', silent=True)



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




from eheritage import views