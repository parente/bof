# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

birds_table = db.Table('birds',
    db.Column('flock_id', db.Integer, db.ForeignKey('flock.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, index=True)
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
    id = db.Column(db.Integer, primary_key=True, index=True)
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
