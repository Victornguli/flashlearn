import os
import click
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from instance.config import app_config

# Try to access the db_settings outside the app context,
# using FLASK_ENV environment setting. Lookup flask_env first then
# check app_config using the flask_env variable. If flask_env is not
# set then default to development config.
FLASK_ENV = os.getenv('FLASK_ENV')

db = app_config.get(FLASK_ENV).DATABASE if app_config.get(FLASK_ENV) else\
	app_config.get('development').DATABASE

engine = create_engine(f"{db}", convert_unicode = True)
db_session = scoped_session(
	sessionmaker(autocommit = False, autoflush = False, bind = engine))

Base = declarative_base()
Base.query = db_session.query_property()


def close_db_session(exception = None):
	db_session.remove()


def init_db():
	import flashlearn.models
	Base.metadata.create_all(bind=engine)


def clear_db():
	import flashlearn.models
	Base.metadata.drop_all(bind = engine)


@click.command('init-db')
@with_appcontext
def init_db_command():
	confirm = click.prompt(
		'The database will be re-defined.\
		\nReply with Y/N to confirm or cancel', type=str)
	if confirm == 'Y' or confirm == 'y':
		init_db()
		click.echo("Initialized the database.")
	else:
		click.echo("Cancelled db init.")


@click.command('clear-db')
@with_appcontext
def clear_db_command():
	confirm = click.prompt(
		'All database tables will be dropped and all data will be lost.\
		\nReply with Y/N to confirm or cancel.', type=str)
	if confirm == 'Y' or confirm == 'y':
		clear_db()
		click.echo('All database tables successfully deleted.')
	else:
		click.echo('Canceled clear_db.')


def init_app(app):
	"""
	Creates engine and initializes session here because of the necessity
	of app_context especially when creating the engine
	"""
	app.teardown_appcontext(close_db_session)
	app.cli.add_command(init_db_command)
	app.cli.add_command(clear_db_command)
