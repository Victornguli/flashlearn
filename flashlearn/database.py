import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from instance.config import app_config


class SQLAlchemyDB:
	"""
	A simplistic abstraction on the manual SQLAlchemy db manipulation.

	By default the database uri used is based on the FLASK_ENV value or defaulting to
	development in the absence of the former.

	Initially the db is initialized with the default database URI but is overridden
	within create_app to initialize it with the same config as the app's config.

	The setup is ideal especially during testing, where there is a need for
	initializing a database in a different environment(testing).
	"""

	database = app_config[os.getenv('FLASK_ENV')].DATABASE_URI if os.getenv('FLASK_ENV')\
		else app_config['development'].DATABASE_URI

	def __init__(self):
		"""
		Initialize the db instance(with scoped session) using default database uri.
		Cli commands without app context will only access the db with this configuration.
		"""
		self.app = None
		self.engine = create_engine(f"{self.database}")
		self.session = scoped_session(
			sessionmaker(autocommit = False, autoflush = False, bind = self.engine))
		self.Base = declarative_base()
		self.Base.query = self.session.query_property()

	def init_with_ctx(self, app):
		"""
		Initialize the db instance with app's context, overriding the default database URI
		"""
		self.app = app
		self.engine = create_engine(f"{self.app.config.get('DATABASE_URI')}")
		self.session = scoped_session(
			sessionmaker(autocommit = False, autoflush = False, bind = self.engine))
		self.Base.query = self.session.query_property()

	def close_session(self, exception = None):
		self.session.remove()

	def init_db(self):
		self.Base.metadata.create_all(bind = self.engine)

	def clear_db(self):
		self.Base.metadata.drop_all(bind = self.engine)
