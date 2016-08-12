# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
from flask import session, jsonify
from flask_oauthlib.client import OAuth


def unauthorized(message):
    """Build a JSON unauthorized tuple."""
    return (jsonify({
        'status': 401,
        'message': message
    }), 401)


oauth = OAuth()
github = oauth.remote_app(
    'github',
    request_token_params=None,
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    app_key='GITHUB'
)


@github.tokengetter
def get_oauth_token():
    """Get the OAuth token from the session."""
    return session.get('oauth_token')
