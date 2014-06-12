from eheritage import app
import string

@app.template_filter('underscoreize')
def underscoreize(s):
    return string.join(s.split(), '_')

@app.template_filter('to_arg')
def to_arg(s):
    return underscoreize(s.lower())

@app.template_filter('apply_filter')
def apply_filter(s, filter_name):
    filters = app.jinja_env.filters
    if filter_name in filters:
        return filters[filter_name](s)
    return s