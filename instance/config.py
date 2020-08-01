import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.dirname(BASE_DIR))


class BaseConfig:
	"""Base config class"""
	SECRET_KEY = os.getenv('secret_key') or 'j^lw01bnhbrl2(k+c626l^n^$hi!&+6xx(ns@m(q*5lj-!xj*9'
	DEBUG = False
	CSRF_ENABLED = True
	FLASK_APP = 'flashlearn'
	DATABASE = os.getenv('DATABASE')
	LOG_FILE = os.getenv('LOG_FILE') or os.path.join(ROOT_DIR, 'flashlearn.log')
	LOG_LEVEL = 20


class DevelopmentConfig(BaseConfig):
	"""Development config class"""
	DEBUG = True
	db_path = os.path.join(BASE_DIR, 'dev_db.sqlite3')
	DATABASE = f'sqlite:///{db_path}'


class TestingConfig(BaseConfig):
	"""Testing config class"""
	DEBUG = True
	TESTING = True
	# db_path = os.path.join(os.path.abspath(os.path.dirname(BASE_DIR)), 'tests/test_db.sqlite3')
	DATABASE = 'sqlite://'
	# Fix to use in-memory db for tests. Replace with above db path to save test data in-file.


class ProductionConfig(BaseConfig):
	"""Production config class"""
	DEBUG = False
	TESTING = False
	db_path = os.path.join(BASE_DIR, 'dev_db.sqlite3')
	DATABASE = f'sqlite:///{db_path}'  # Replace with production database..


app_config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig
}
