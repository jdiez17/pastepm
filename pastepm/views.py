from flask.views import MethodView
from flask import redirect, url_for, request, render_template, flash, abort, session
from pygments.lexers import guess_lexer, get_lexer_for_filename
from pygments.util import ClassNotFound

from pastepm.models import Paste, User, Purchase
from pastepm.utils import decode_id, encode_id, guess_extension
from pastepm.database import db_session
from pastepm.cache import memoize
from pastepm.payment import using_paypal, paypal

import sqlalchemy

class PastePost(MethodView):
    def post(self):
        if "content" not in request.form.keys():
            return redirect(url_for('index')) 

        content = request.form['content']

        p = Paste(content)
        db_session.add(p)
        db_session.commit()

        extension = guess_extension(content)

        return url_for('view', id=encode_id(p.id), extension=extension)

class PasteView(MethodView):
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
    def get(self, id, extension="txt"):
        paste = self._get_content(id)

        if paste == None:
            abort(404)

        try:
            language = self.get_language(id, paste, extension)
        except ClassNotFound:
            return redirect(url_for('view', id=id, extension="txt"))

        return render_template("index.html", paste=paste, language=language, id=id)

class RawView(PasteView):
    @memoize(time=3600)
    def get(self, id, extension="txt"):
        paste = self._get_content(id)
        return "<pre>%s</pre>" % paste

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
        return render_template("register.html", payment=using_paypal)

    def post(self):
        if "username" not in request.form or "password" not in request.form:
            return redirect(url_for('register'))

        username = request.form['username']
        password = request.form['password']

        if len(password) < 4:
            flash("Password must be greater than 4 characters", "error")
            return redirect(url_for('register'))

        try:
            u = User(username, password, using_paypal)
            db_session.add(u)
            db_session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash("Username taken", "error")
            return redirect(url_for('register'))

        if using_paypal:
            session['payment_target_id'] = u.id
            return render_template("checkout.html")
        else:
            return render_template("confirm.html") 

class PayPalStart(MethodView):
    def post(self):
        if not "amt" in request.form:
            flash("You must specify the amount to pay", "error")
            return render_template("checkout.html")

        kw = {
            'amt': request.form['amt'], 
            'currencycode': 'USD',
            'returnurl': url_for('paypal_confirm', _external=True), 
            'cancelurl': url_for('index', _external=True),
            'paymentaction': 'Sale'
        }

        setexp_response = paypal.set_express_checkout(**kw)
        if setexp_response['ACK'] == 'Success':
            p = Purchase(session['payment_target_id'], setexp_response.token, kw['amt'])
            db_session.add(p)
            db_session.commit()

            return redirect(paypal.generate_express_checkout_redirect_url(setexp_response.token))
        else:
            flash("Sorry, something went wrong. Try again.", "error")
            return render_template("checkout.html")

class PayPalConfirm(MethodView):
    def get(self):
       getexp_response = paypal.get_express_checkout_details(token=request.args.get('token', ''))
       
       if getexp_response['ACK'] == 'Success':
           return render_template("confirm_payment.html", token=getexp_response['TOKEN']) 
       else:
           return render_template("paypal_error.html", message=getexp_response['ACK'])

class PayPalDo(MethodView):
    def get(self, token):
        getexp_response = paypal.get_express_checkout_details(token=token)
        kw = {
            'amt': getexp_response['AMT'],
            'currencycode': getexp_response['CURRENCYCODE'],
            'paymentaction': 'Sale',
            'token': token,
            'payerid': getexp_response['PAYERID']
        }
        paypal.do_express_checkout_payment(**kw)

        return redirect(url_for('paypal_status', token=kw['token']))

class PayPalStatus(MethodView):
    def get(self, token):
        checkout_response = paypal.get_express_checkout_details(token=token)

        if checkout_response['CHECKOUTSTATUS'] == 'PaymentActionCompleted':
            p = Purchase.query.filter_by(token=token).one()
            u = User.query.get(p.uid)
            p.confirm_payment()
            u.activated = True
            db_session.commit()

            return render_template("confirm.html")
        else:
            return render_template("paypal_error.html", message=checkout_response['CHECKOUTSTATUS'])

