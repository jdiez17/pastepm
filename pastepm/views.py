from flask.views import View, MethodView
from flask import redirect, url_for, request, render_template, flash, abort
from pygments.lexers import guess_lexer, get_lexer_for_filename
from pygments.util import ClassNotFound

from pastepm.models import Paste, User
from pastepm.utils import decode_id, encode_id, guess_extension
from pastepm.database import db_session
from pastepm.cache import memoize

import sqlalchemy

class PastePost(View):
    methods = ["POST"]
    
    def dispatch_request(self):
        if "content" not in request.form.keys():
            return redirect(url_for('index')) 

        content = request.form['content']

        p = Paste(content)
        db_session.add(p)
        db_session.commit()

        extension = guess_extension(content)

        return redirect(url_for('view', id=encode_id(p.id), extension=extension))

class PasteView(View):
    def _get_content(self, id):
        id = decode_id(id)
        paste = Paste.query.get(id)

        return paste

    def _get_lexer(self, filename):
        try:
            lexer = get_lexer_for_filename(filename)
        except ClassNotFound:
            raise

        return lexer

    @memoize(time=3600)
    def dispatch_request(self, id, extension="txt"):
        paste = self._get_content(id)

        if paste == None:
            abort(404)

        try:
            language = self.get_language(id, paste, extension)
        except ClassNotFound:
            return redirect(url_for('view', id=id, extension="txt"))

        return render_template("paste.html", paste=paste, language=language)

class PasteViewWithExtension(PasteView):
    def get_language(self, id, content, extension="txt"):
        filename = "%s.%s" % (id, extension) 
        return self._get_lexer(filename).aliases[0]

class PasteViewWithoutExtension(PasteView):
    def get_language(self, id, content, extension="txt"):
        extension = guess_extension(str(content))
        return self._get_lexer("%s.%s" % (id, extension)).aliases[0] 

class RegisterView(MethodView):
    def get(self):
        return render_template("register.html")

    def post(self):
        if "username" not in request.form or "password" not in request.form:
            return redirect(url_for('register'))

        username = request.form['username']
        password = request.form['password']

        if len(password) < 4:
            flash("Password must be greater than 4 characters", "error")
            return redirect(url_for('register'))

        try:
            u = User(username, password)
            db_session.add(u)
            db_session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash("Username taken", "error")
            return redirect(url_for('register'))

        return "OK I guess"
