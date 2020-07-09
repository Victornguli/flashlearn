import os
from flask import Flask, jsonify, session, g
from sqlalchemy import create_engine

from instance.config import app_config
from flashlearn.decorators import login_required
from flashlearn.database import SQLAlchemyDB

db = SQLAlchemyDB()


def create_app(config = None):
    app = Flask(__name__, instance_relative_config=True)
    if config:
        flask_env = config  # Preferably for use in the testing environment
    else:
        flask_env = os.getenv('FLASK_ENV')
    if not flask_env:
        flask_env = 'development'
    os.environ['FLASK_ENV'] = flask_env
    conf_mapping = app_config.get(flask_env, '')
    if not conf_mapping:
        raise ValueError('Invalid environment settings')
    app.config.from_object(conf_mapping)

    try:
        # Creates instance_path if the directory DNE
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    @login_required
    def index():
        user = g.user
        return jsonify({
            'username': user.username
        })

    from flashlearn.database import init_app
    init_app(app)  # Setup database with app_context

    db.init(app)

    from flashlearn.auth import bp
    app.register_blueprint(bp)

    return app
