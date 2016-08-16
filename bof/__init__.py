# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
import os
from flask import Flask
from flask_sslify import SSLify
from .model import db
from .auth import oauth
from .ui import ui_bp
from .api import api_bp

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                  'sqlite:////tmp/bof.db')
app.config['APP_TITLE'] = os.getenv('APP_TITLE', 'Birds of a Feather')
app.config['GITHUB_CONSUMER_KEY'] = os.getenv('GITHUB_CONSUMER_KEY')
app.config['GITHUB_CONSUMER_SECRET'] = os.getenv('GITHUB_CONSUMER_SECRET')

app.register_blueprint(api_bp)
app.register_blueprint(ui_bp)

db.init_app(app)
oauth.init_app(app)
if 'VCAP_SERVICES' in os.environ:
    SSLify(app)
