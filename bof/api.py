# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
from functools import wraps
from flask import Blueprint, jsonify, request, session, g
from .model import db, User, Flock
from .auth import unauthorized

api_bp = Blueprint('api', __name__)


def require_auth(f):
    @wraps(f)
    def _require_auth(*args, **kwargs):
        try:
            username = session['username']
        except KeyError:
            return unauthorized('action requires authentication')
        user = User.query.filter_by(username=username).first()
        # stale user reference
        if user is None:
            return unauthorized('user does not exist')
        # banned users are not authenticated
        elif user.banned:
            return unauthorized('user is banned')
        g.user = user
        return f(*args, **kwargs)
    return _require_auth


@api_bp.route('/api/flocks')
def list_flocks():
    flocks = Flock.query.all()
    return jsonify({
        'results': [flock.to_dict() for flock in reversed(flocks)]
    })


@api_bp.route('/api/flocks', methods=['POST'])
@require_auth
def create_flock():
    content = request.json
    flock = Flock(name=content['name'],
                  description=content['description'],
                  where=content['where'],
                  when=content['when'],
                  leader=g.user)
    db.session.add(flock)
    try:
        db.session.commit()
    finally:
        db.session.rollback()

    return (jsonify(flock.to_dict()), 201)


# need to support POST because polymer doesn't send JSON bodies with PUT
@api_bp.route('/api/flocks/<fid>', methods=['PUT', 'POST'])
@require_auth
def update_flock(fid):
    content = request.json

    # check if user has access to update
    flock = Flock.query.get(fid)
    if flock.leader.username != g.user.username and not g.user.admin:
        return unauthorized('{} cannot update flock'.format(g.user.username))

    flock.name = content.get('name', flock.name)
    flock.description = content.get('description', flock.name)
    flock.when = content.get('when', flock.when)
    flock.where = content.get('where', flock.where)
    try:
        db.session.commit()
    finally:
        db.session.rollback()

    return (jsonify(flock.to_dict()), 200)


@api_bp.route('/api/flocks/<fid>', methods=['DELETE'])
@require_auth
def delete_flock(fid):
    # check if user has access to delete
    flock = Flock.query.get(fid)
    if flock.leader.username != g.user.username and not g.user.admin:
        return unauthorized('{} cannot delete flock'.format(g.user.username))

    db.session.delete(flock)
    try:
        db.session.commit()
    finally:
        db.session.rollback()

    return '', 204


@api_bp.route('/api/flocks/<fid>/birds', methods=['POST'])
@require_auth
def join_flock(fid):
    flock = Flock.query.get(fid)
    if g.user not in flock.birds:
        flock.birds.append(g.user)
    try:
        db.session.commit()
    finally:
        db.session.rollback()

    return (jsonify(flock.to_dict()), 200)


@api_bp.route('/api/flocks/<fid>/birds/self', methods=['DELETE'])
@require_auth
def leave_flock(fid):
    flock = Flock.query.get(fid)
    if g.user in flock.birds:
        flock.birds.remove(g.user)
    try:
        db.session.commit()
    finally:
        db.session.rollback()

    return (jsonify(flock.to_dict()), 200)
