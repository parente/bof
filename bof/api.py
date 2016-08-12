# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
from flask import Blueprint, jsonify, request, session
from .model import db, User, Flock
from .auth import unauthorized

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/flocks')
def list_flocks():
    flocks = Flock.query.all()
    return jsonify({
        'results': [flock.to_dict() for flock in reversed(flocks)]
    })


@api_bp.route('/api/flocks', methods=['POST'])
def create_flock():
    content = request.json

    # authenticated user is the leader of the flock
    try:
        username = session['username']
    except KeyError:
        return unauthorized('must be logged in to create a flock')
    user = User.query.filter_by(username=username).first()

    flock = Flock(name=content['name'],
                  description=content['description'],
                  where=content['where'],
                  when=content['when'],
                  leader=user)
    db.session.add(flock)
    db.session.commit()

    return (jsonify(flock.to_dict()), 201)


# need to support POST because polymer doesn't send JSON bodies with PUT
@api_bp.route('/api/flocks/<fid>', methods=['PUT', 'POST'])
def update_flock(fid):
    content = request.json

    # authenticated user is the leader of the flock
    try:
        username = session['username']
    except KeyError:
        return unauthorized('must be logged in to update a flock')
    user = User.query.filter_by(username=username).first()

    # check if user has access to update
    flock = Flock.query.get(fid)
    if flock.leader.username != username and not user.admin:
        return unauthorized('{} cannot delete flock'.format(username))

    flock.name = content.get('name', flock.name)
    flock.description = content.get('description', flock.name)
    flock.when = content.get('when', flock.when)
    flock.where = content.get('where', flock.where)
    db.session.commit()

    return (jsonify(flock.to_dict()), 200)


@api_bp.route('/api/flocks/<fid>', methods=['DELETE'])
def delete_flock(fid):
    # authenticated user is the leader of the flock
    try:
        username = session['username']
    except KeyError:
        return unauthorized('must be logged in to delete a flock')
    user = User.query.filter_by(username=username).first()

    # check if user has access to delete
    flock = Flock.query.get(fid)
    if flock.leader.username != username and not user.admin:
        return unauthorized('{} cannot delete flock'.format(username))

    db.session.delete(flock)
    db.session.commit()
    return '', 204


@api_bp.route('/api/flocks/<fid>/birds', methods=['POST'])
def join_flock(fid):
    # authenticated user is the leader of the flock
    try:
        username = session['username']
    except KeyError:
        return unauthorized('must be logged in to join a flock')
    user = User.query.filter_by(username=username).first()

    flock = Flock.query.get(fid)
    if username not in flock.birds:
        flock.birds.append(user)
    db.session.commit()

    return (jsonify(flock.to_dict()), 200)


@api_bp.route('/api/flocks/<fid>/birds/self', methods=['DELETE'])
def leave_flock(fid):
    # authenticated user is the leader of the flock
    try:
        username = session['username']
    except KeyError:
        return unauthorized('must be logged in to leave a flock')
    user = User.query.filter_by(username=username).first()

    flock = Flock.query.get(fid)
    if user in flock.birds:
        flock.birds.remove(user)
    db.session.commit()

    return (jsonify(flock.to_dict()), 200)
