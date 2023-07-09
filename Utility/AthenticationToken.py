import os
from flask import request, jsonify


# Verify if the provided token is valid
def verify_token(token):
    secret_key = os.environ.get("AUTH_KEY")
    return secret_key == token


# Decorator to require authentication for protected routes
def require_token(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not verify_token(token):
            return jsonify({'error': 'Unauthorized access'}), 401
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
