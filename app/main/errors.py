from flask import render_template
from . import page


@page.app_errorhandler(404)
def file_not_found(e):
    return render_template('404.html'), 404