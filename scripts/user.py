"""Ban / unban users."""
# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
import sys
sys.path.append('./')
from bof import app
from bof.model import db, User, Flock


def usage():
    print('usage: {} ban|unban <username>'.format(sys.argv[0]))


if len(sys.argv) < 3:
    usage()
    sys.exit(1)

action = sys.argv[1]
username = sys.argv[2]

if action not in ['ban', 'unban']:
    usage()
    sys.exit(1)

with app.app_context():
    user = User.query.filter_by(username=username).first()
    user.banned = True if action == 'ban' else False
    db.session.commit()
    print(user.to_dict())
