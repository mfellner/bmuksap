# -*- coding: utf-8 -*-

import os

from flask import Flask

from app.api import bp, api


def create_app(debug=False):
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.secret_key = os.urandom(24)
    app.debug = debug

    app.register_blueprint(bp)
    app.register_blueprint(api)

    return app


if __name__ == '__main__':
    app = create_app(debug=True)
    app.test_request_context().push()
    app.run()
