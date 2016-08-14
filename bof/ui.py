# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
from flask import (Blueprint, render_template, request, session, url_for,
                   redirect, current_app)
from .model import User, db
from .auth import unauthorized, github

ui_bp = Blueprint('ui', __name__, static_folder='static')


@ui_bp.route('/login')
def login():
    return github.authorize(callback=url_for('ui.authorized', _external=True))


@ui_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('ui.index'))


@ui_bp.route('/login/github/authorization')
def authorized():
    resp = github.authorized_response()

    if resp is None:
        return unauthorized('{}: {}'.format(
                request.args['error'], request.args['error_description']
            )
        )

    # format required to fetch user profile
    session['oauth_token'] = (resp['access_token'], '')
    me = github.get('user')
    username = session['username'] = me.data['login']
    session['avatar_url'] = me.data.get('avatar_url', '')
    session['oauth_provider'] = 'github'

    # create a user model if one does not exist
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username)
        db.session.add(user)
        db.session.commit()
    elif user.banned:
        # clear the session if the user is banned
        session.clear()

    return redirect(url_for('ui.index'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('oauth_token')


@ui_bp.route('/')
def index():
    username = session.get('username', '')
    avatar_url = session.get('avatar_url', '')
    return render_template('index.html', username=username,
                           avatar_url=avatar_url,
                           title=current_app.config['APP_TITLE'])
