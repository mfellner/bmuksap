# -*- coding: utf-8 -*-

from flask import Flask

from bmuksap.api import api


def create_app(debug=False):
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.debug = debug

    app.register_blueprint(api, url_prefix='/')

    return app
