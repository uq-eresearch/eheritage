from eheritage import app
from flask import request, url_for
import string

@app.template_filter('underscoreize')
def underscoreize(s):
    """Replace whitespace with underscores"""
    return string.join(s.split(), '_')

@app.template_filter('to_arg')
def to_arg(s):
    """Lower case and replace whitespace with underscores"""
    return underscoreize(s.lower())

@app.template_filter('apply_filter')
def apply_filter(s, filter_name):
    """Apply the named filter"""
    filters = app.jinja_env.filters
    if filter_name in filters:
        return filters[filter_name](s)
    return s


@app.template_filter('head')
def head(s, num=5):
    return s[:num]

@app.template_global()
def url_for_custom_params(endpoint, **kwargs):
    """Add or subtract query params when generating a url

    Similar to url_for()
    """
    args = dict(request.args)
    args.update(kwargs)

    # Filter out blank values
    args = {key: value for (key, value) in args.items() if value}
    return url_for(endpoint, **args)