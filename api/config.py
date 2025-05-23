import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "the-testing-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "the-testing-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
