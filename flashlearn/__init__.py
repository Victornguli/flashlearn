import os
from flask import Flask
from instance.config import app_config


def create_app(config = None):
    app = Flask(__name__, instance_relative_config=True)
    flask_env = os.getenv('FLASK_ENV')
    if not flask_env:
        flask_env = 'development'
    conf_mapping = app_config.get(flask_env, '')
    if not conf_mapping:
        raise ValueError('Invalid environment settings')
    app.config.from_object(conf_mapping)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():
        return 'Hello, World!'

    from flashlearn.db import init_app, setup_engine_with_ctx
    setup_engine_with_ctx(app)
    init_app(app)

    return app
