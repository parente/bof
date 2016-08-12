# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
import os
from flask import (Flask, render_template, jsonify, request, url_for, session,
    redirect)
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
    'sqlite:////tmp/bof.db')
app.config['APP_TITLE'] = os.getenv('APP_TITLE', 'Birds of a Feather')
app.config['APP_LOGO_URL'] = os.getenv('APP_LOGO_URL')
app.config['GITHUB_CONSUMER_KEY'] = os.environ['GITHUB_CONSUMER_KEY']
app.config['GITHUB_CONSUMER_SECRET'] = os.environ['GITHUB_CONSUMER_SECRET']

from model import db
from ui import oauth

db.init_app(app)
oauth.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
