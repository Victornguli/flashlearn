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

	database = app_config[os.getenv('FLASK_ENV')].DATABASE if os.getenv('FLASK_ENV')\
		else app_config['development'].DATABASE

	def __init__(self):
		self.app = None
		self.engine = create_engine(f"{self.database}")
		self.session = scoped_session(
			sessionmaker(autocommit = False, autoflush = False, bind = self.engine))
		self.Base = declarative_base()
		self.Base.query = self.session.query_property()

	def init(self, app):
		self.app = app
		self.engine = create_engine(f"{self.app.config.get('DATABASE')}")
		self.session = scoped_session(
			sessionmaker(autocommit = False, autoflush = False, bind = self.engine))
		self.Base.query = self.session.query_property()

	def close_session(self, exception = None):
		self.session.remove()

	def init_db(self):
		self.Base.metadata.create_all(bind = self.engine)

	def clear_db(self):
		self.Base.metadata.drop_all(bind = self.engine)
