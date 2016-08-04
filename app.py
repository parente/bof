import os
from flask import (Flask, render_template, jsonify, request, url_for, session,
    redirect)
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
    'sqlite:////tmp/bof.db')

db = SQLAlchemy(app)

birds_table = db.Table('birds',
    db.Column('flock_id', db.Integer, db.ForeignKey('flock.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    banned = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, banned=False, admin=False):
        self.username = username
        self.banned = banned
        self.admin = admin

    def to_dict(self):
        return {
            'username': self.username,
            'banned': self.banned,
            'admin': self.admin
        }

class Flock(db.Model):
    __tablename__ = 'flock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(256))
    where = db.Column(db.String(64))
    when = db.Column(db.String(64))
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    leader = db.relationship('User')
    birds = db.relationship('User', secondary=birds_table,
        backref=db.backref('flocks', lazy='joined')
    )

    def __init__(self, name, description, when, where, leader):
        self.name = name
        self.description = description
        self.where = where
        self.when = when
        self.leader = leader

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'where': self.where,
            'when': self.when,
            'leader': self.leader.username,
            'birds': [bird.username for bird in self.birds]
        }

oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    consumer_key=os.getenv('GITHUB_CLIENT_ID'),
    consumer_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    request_token_params=None,
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

@app.route('/api/auth/github', methods=["POST", "GET"])
def login():
    return github.authorize(callback=url_for('authorized', _external=True))

@app.route('/api/auth/github', methods=["DELETE"])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/auth/github/authorization')
def authorized():
    resp = github.authorized_response()

    if resp is None:
        return unauthorized('{}: {} cannot delete flock'.format(
                request.args['error'], request.args['error_description']
            )
        )

    # format required to fetch user profile
    session['oauth_token'] = (resp['access_token'], '')
    me = github.get('user')
    username = session['username'] = me.data['login']
    session['oauth_provider'] = 'github'

    # create a user model if one does not exist
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username)
        db.session.add(user)
        db.session.commit()

    return redirect(url_for('index'))

@github.tokengetter
def get_github_oauth_token():
    return session.get('oauth_token')

def unauthorized(message):
    return (jsonify({
        'status': 401,
        'message': message
    }), 401)

@app.route('/')
def index():
    username = session.get('username', '')
    return render_template('index.html', username=username)

@app.route('/api/flocks')
def list_flocks():
    flocks = Flock.query.all()
    return jsonify({
        'results' : [flock.to_dict() for flock in reversed(flocks)]
    })

@app.route('/api/flocks', methods=['POST'])
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
        leader=user
    )
    db.session.add(flock)
    db.session.commit()

    return (jsonify(flock.to_dict()), 201)

# need to support POST because polymer doesn't send JSON bodies with PUT
@app.route('/api/flocks/<fid>', methods=['PUT', 'POST'])
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

@app.route('/api/flocks/<fid>', methods=['DELETE'])
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

@app.route('/api/flocks/<fid>/birds', methods=['POST'])
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

@app.route('/api/flocks/<fid>/birds/self', methods=['DELETE'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
