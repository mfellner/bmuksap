# -*- coding: utf-8 -*-

from flask import Blueprint, Response, render_template, request, redirect, session

from app.control import BmukSapException, load_raw_pdf


bp = Blueprint('errors', __name__)


@bp.app_errorhandler(404)
def handle_404(e):
    clear_session()
    return render_template('error.html', error=400), 400


@bp.app_errorhandler(500)
def handle_500(e):
    clear_session()
    return render_template('error.html', error=e.message), 500


api = Blueprint('api', __name__)


@api.route('/')
def login():
    return render_template('login.html')


@api.route('/pdf', methods=['GET', 'POST'])
def pdf():
    if request.method == 'GET':
        clear_session()
        return redirect('/', 302)
    else:
        session['username'] = request.form['inputUsername'].split('@')[0]
        session['domain'] = request.form['inputUsername'].split('@')[1]
        session['password'] = request.form['inputPassword']
        # return render_template('pdf.html')
        return redirect('/pdf/result.pdf', 302)


@api.route('/pdf/result.pdf')
def pdf_file():
    if not 'username' in session:
        return redirect('/', 302)

    try:
        raw_pdf = load_raw_pdf(session)
        return Response(raw_pdf, mimetype='application/pdf')
    except BmukSapException as error:
        return Response(error.message, mimetype='text/html')
    finally:
        clear_session()


def clear_session():
    session.pop('username', None)
    session.pop('domain', None)
    session.pop('password', None)
