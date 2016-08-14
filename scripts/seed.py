"""Create tables if they do not exists."""
# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
import sys
sys.path.append('./')
from bof import app
from bof.model import db, User, Flock

with app.app_context():
    db.create_all()
