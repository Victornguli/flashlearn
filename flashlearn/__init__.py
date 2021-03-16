import os
import logging
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, url_for
from logging.handlers import RotatingFileHandler
from instance.config import app_config
from flashlearn.decorators import login_required, redis_cache

session_options = {"expire_on_commit": False}
db = SQLAlchemy(session_options=session_options)
csrf = CSRFProtect()
redis_cache = redis_cache


def create_app(config=None):
    """
    Create app factory function to initialize the Flask App
    :param config: The configuration name, if required:
        - Can be development, testing or production.
        - You can add more environments by following the similar
          structure defined in instance/config.py
    :type config: str | None
    :return: Flask app
    :rtype: Flask
    """
    app = Flask(__name__, instance_relative_config=True)

    # Setup configs
    if config:
        flask_env = config
    else:
        flask_env = os.getenv("FLASK_ENV")
    if not flask_env:
        flask_env = "development"
    os.environ["FLASK_ENV"] = flask_env
    conf_mapping = app_config.get(flask_env, "")
    if not conf_mapping:
        raise ValueError("Invalid environment settings")
    app.config.from_object(conf_mapping)

    # Setup logging
    if not app.testing:
        formatter = logging.Formatter(
            "[%(asctime)s] - {%(pathname)s:%(lineno)d} %(levelname)s" "- %(message)s"
        )
        handler = RotatingFileHandler(
            app.config.get("LOG_FILE"), maxBytes=10000000, backupCount=1
        )
        handler.setLevel(logging.getLevelName(app.config.get("LOG_LEVEL", 20)))
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

    try:
        # Creates instance_path if the directory DNE
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    @login_required
    def index():
        # user = g.user
        # TODO: Add index code
        return redirect(url_for("core.decks"))

    db.init_app(app)
    csrf.init_app(app)
    # Commands and Blueprint registration needs to be after db init..
    register_blueprints_and_commands(app)

    return app


def register_blueprints_and_commands(app):
    from flashlearn.user import user, routes
    from flashlearn.core import core, routes  # noqa
    from flashlearn.commands import register_commands

    register_commands(app)
    app.register_blueprint(user)
    app.register_blueprint(core)
