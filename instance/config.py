import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.dirname(BASE_DIR))

WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"


class BaseConfig:
    """Base config class"""

    SECRET_KEY = (
        os.getenv("secret_key") or "j^lw01bnhbrl2(k+c626l^n^$hi!&+6xx(ns@m(q*5lj-!xj*9"
    )
    DEBUG = False
    USE_REDIS_CACHE = False
    CSRF_ENABLED = True
    FLASK_APP = "flashlearn"
    sqlite_db_path = os.path.join(BASE_DIR, "dev_db.sqlite3")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", f"{prefix}{sqlite_db_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    LOG_FILE = os.getenv("LOG_FILE") or os.path.join(ROOT_DIR, "flashlearn.log")
    LOG_LEVEL = 20


class DevelopmentConfig(BaseConfig):
    """Development config class"""

    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing config class"""

    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Fix to use in-memory db for tests.
    # Replace with above db path to save test data in-file.


class ProductionConfig(BaseConfig):
    """Production config class"""

    DEBUG = False
    TESTING = False


app_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
