import os
from flask import Flask


def create_app(config = None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = 'dummy',
    )
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():
        return 'Hello, World!'

    from flashlearn.db import init_app
    init_app(app)

    return app
