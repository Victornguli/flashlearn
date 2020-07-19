import os
from flask import Flask, jsonify, g
from instance.config import app_config
from flashlearn.decorators import login_required
from flashlearn.database import SQLAlchemyDB

db = SQLAlchemyDB()


def create_app(config = None):
    """
    Create app factory function to initialize the Flask App
    :param config: The configuration name, if required:
        - can be development, testing or production.
        - You can add more environments by  following the similar
          structure defined in instance/config.py
    :type config: str | None
    :return: Flask app
    :rtype: Flask
    """
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
    def index():
        # user = g.user
        # TODO: Add index code
        return "Index"

    from flashlearn.commands import register_commands
    register_commands(app)  # Register app cli commands

    db.init_with_ctx(app)  # Initialize Db with the app context
    app.teardown_appcontext(db.close_session)

    from flashlearn.auth import bp
    app.register_blueprint(bp)

    from flashlearn.core import bp, routes
    app.register_blueprint(bp)
    return app
