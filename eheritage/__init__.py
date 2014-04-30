from flask import Flask
from eheritage.utils import IterableAwareEncoder

app = Flask(__name__)
app.config.from_object('config')

app.json_encoder = IterableAwareEncoder

from eheritage import views