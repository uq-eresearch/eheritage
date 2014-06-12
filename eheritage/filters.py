from eheritage import app
import string

@app.template_filter('underscoreize')
def underscoreize(s):
    return string.join(s.split(), '_')

@app.template_filter('to_arg')
def to_arg(s):
    return underscoreize(s.lower())