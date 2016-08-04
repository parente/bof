import os
from flask import Flask, render_template, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/bof.db')
db = SQLAlchemy(app)

birds_table = db.Table('birds',
    db.Column('flock_id', db.Integer, db.ForeignKey('flock.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)

    def __init__(self, username):
        self.username = username

    def to_dict(self):
        return {
            'username': self.username
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/flocks')
def list_flocks():
    flocks = Flock.query.all()
    return jsonify({'results' : [flock.to_dict() for flock in reversed(flocks)]})

@app.route('/api/flocks', methods=['POST'])
def create_flock():
    content = request.json

    # TODO: replace with authed user
    user = User.query.filter_by(username='nobody').first()
    print(user)

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

    # TODO: replace with authed user
    username = 'nobody'
    user = User.query.filter_by(username=username).first()

    # check if user has access to update
    flock = Flock.query.get(fid)
    if flock.leader.username != username:
        return (jsonify({
            'status': 401,
            'message': '{} cannot delete flock'.format(username)
        }), 401)

    flock.name = content.get('name', flock.name)
    flock.description = content.get('description', flock.name)
    flock.when = content.get('when', flock.when)
    flock.where = content.get('where', flock.where)
    db.session.commit()

    return (jsonify(flock.to_dict()), 200)

@app.route('/api/flocks/<fid>', methods=['DELETE'])
def delete_flock(fid):
    # TODO: replace with authed user
    username = 'nobody'
    user = User.query.filter_by(username=username).first()

    # check if user has access to delete
    flock = Flock.query.get(fid)
    if flock.leader.username != username:
        return (jsonify({
            'status': 401,
            'message': '{} cannot delete flock'.format(username)
        }), 401)

    db.session.delete(flock)
    db.session.commit()
    return '', 204

@app.route('/api/flocks/<fid>/birds', methods=['POST'])
def join_flock(fid):
    # TODO: replace with authed user
    username = 'nobody'
    user = User.query.filter_by(username=username).first()

    flock = Flock.query.get(fid)
    if username not in flock.birds:
        flock.birds.append(user)
    db.session.commit()

    return (jsonify(flock.to_dict()), 200)

@app.route('/api/flocks/<fid>/birds/self', methods=['DELETE'])
def leave_flock(fid):
    # TODO: replace with authed user
    username = 'nobody'
    user = User.query.filter_by(username=username).first()

    flock = Flock.query.get(fid)
    if user in flock.birds:
        flock.birds.remove(user)
    db.session.commit()

    return (jsonify(flock.to_dict()), 200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
