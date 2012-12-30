from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from pastepm.database import db_session
from pastepm.views import PastePost, PasteViewWithExtension, PasteViewWithoutExtension, RegisterView
from pastepm.config import config

import os

app = Flask(__name__)

@app.context_processor
def utility_processor():
    def do_highlight(language, code, lines=True):
        lex = get_lexer_by_name(language, stripall=False)
        formatter = HtmlFormatter(linenos=lines, cssclass="source")
        code = highlight(code, lex, formatter)

        return code 

    def get_style(style="default"):
        return HtmlFormatter(style=style).get_style_defs('.highlight')

    return {'highlight': do_highlight, 'get_style': get_style}

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/")
def index():
    return render_template("index.html") 

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

url_mapping = {
    'post': {
        'url': '/post', 
        'cls': PastePost
    },
    'view': {
        'url': '/<string:id>.<string:extension>', 
        'cls': PasteViewWithExtension
    },
    'view2': {
        'url': '/<string:id>',
        'cls': PasteViewWithoutExtension
    },
    'register': {
        'url': '/register',
        'cls': RegisterView
    }
}

for view in url_mapping:
    mapping = url_mapping[view]
    app.add_url_rule(mapping['url'], view_func=mapping['cls'].as_view(view))

app.secret_key = config.get('security', 'secret_key')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8337, debug=True)

