# auth.py
from functools import wraps
from flask import session, redirect, url_for
from AppConstants.Constants import Constants

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if Constants.USER not in session:
            return redirect(url_for(Constants.BLISSMAKE_LOGIN))
        return f(*args, **kwargs)
    return decorated_function
