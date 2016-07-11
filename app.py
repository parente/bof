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

    def to_json(self):
        return {
            'username': self.username
        }

class Flock(db.Model):
    __tablename__ = 'flock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512))
    where = db.Column(db.String(128))
    when = db.Column(db.String(128))
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

    def to_json(self):
        return {
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
    return jsonify({'results' : [flock.to_json() for flock in flocks]})

@app.route('/api/flocks', methods=['POST'])
def create_flock():
    content = request.json
    print(content)
    return (jsonify({
        'id': 1,
        'link': url_for('delete_flock', fid=1)
    }), 201)

@app.route('/api/flocks/<fid>', methods=['DELETE'])
def delete_flock(fid):
    return 'TODO: update flock ' + fid

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
