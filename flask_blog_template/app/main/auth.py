# auth.py
from flask_httpauth import HTTPTokenAuth
from .models import User

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    user = User.verify_auth_token(token)
    if user:
        return user

