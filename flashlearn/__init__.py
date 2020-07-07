import os
from flask import Flask
from instance.config import app_config


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    flask_env = os.getenv('FLASK_ENV')
    if not flask_env:
        flask_env = 'development'
    os.environ['FLASK_ENV'] = flask_env
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

    from flashlearn.db import init_app
    init_app(app)

    return app
