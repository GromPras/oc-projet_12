import sqlalchemy as sa
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app import db
from app.models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email, password):
    user = db.session.scalar(sa.select(User).where(User.email == email))
    if user and user.check_password(password):
        return user


@token_auth.verify_token
def verify_token(token):
    # TODO: add check_token method to User class
    return User.check_token(token) if token else None
