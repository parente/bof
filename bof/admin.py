"""Admin control CLI."""
# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
import click
from prettytable import PrettyTable
from . import app
from .model import db, User, Flock, Location


@click.group()
def admin():
    """Admin access to BoF data."""
    pass


@admin.group()
def user():
    """Manage users."""
    pass


@user.command()
def list():
    """List all registered users."""
    table = PrettyTable(['id', 'username', 'banned', 'admin'])
    with app.app_context():
        for user in User.query.all():
            table.add_row([user.id, user.username, user.banned, user.admin])
    click.echo(table)


def apply_ban(username, ban):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        user.banned = ban
        db.session.commit()
        return user.to_dict()


@user.command()
@click.argument('username')
def ban(username):
    """Ban a user."""
    user = apply_ban(username, True)
    click.echo(user)


@user.command()
@click.argument('username')
def unban(username):
    """Unban a user."""
    user = apply_ban(username, False)
    click.echo(user)


@admin.group()
def flock():
    """Manage flocks."""
    pass


@flock.command()
def list():
    """List all flocks."""
    table = PrettyTable(['id', 'name', 'leader', 'birds'])
    with app.app_context():
        for flock in Flock.query.all():
            table.add_row([flock.id, flock.name, flock.leader.username,
                           len(flock.birds)])
    click.echo(table)


@flock.command()
@click.argument('id')
@click.confirmation_option(prompt='Are you sure you want to delete the flock?')
def remove(id):
    """Remove a flock."""
    with app.app_context():
        flock = Flock.query.get(id)
        db.session.delete(flock)
        db.session.commit()


@flock.command()
@click.argument('id')
def edit(id):
    """Edit a flock."""
    with app.app_context():
        flock = Flock.query.get(id)
        flock.name = click.prompt('Name', default=flock.name)
        flock.description = click.prompt('Description',
                                         default=flock.description)
        flock.when = click.prompt('When', default=flock.when)
        flock.where = click.prompt('Where', default=flock.where)
        db.session.commit()


@admin.group()
def location():
    """Manage location suggestions."""
    pass


@location.command()
def list():
    """List location suggestions."""
    table = PrettyTable(['id', 'name', 'image'])
    with app.app_context():
        for loc in Location.query.all():
            table.add_row([loc.id, loc.name, loc.image_url])
    click.echo(table)


@location.command()
@click.option('--name', '-n', prompt='Location name', help='Location name')
@click.option('--image_url', '-i', prompt='Location image URL', help='Location image URL')
def add(name, image_url):
    """Add a location suggestion."""
    with app.app_context():
        loc = Location(name, image_url)
        db.session.add(loc)
        db.session.commit()
        id = loc.id
    click.echo('Created location {}'.format(id))


@location.command()
@click.argument('id')
@click.confirmation_option(prompt='Are you sure you want to delete this location?')
def remove(id):
    """Remove a location suggestion."""
    with app.app_context():
        loc = Location.query.get(id)
        db.session.delete(loc)
        db.session.commit()


@admin.group()
def data():
    """Manage database."""
    pass


@data.command()
def examples():
    """Drop / create tables, and seed examples."""
    with app.app_context():
        click.confirm('Are you sure you want to reset {}?'.format(db.engine),
                      abort=True)
        db.drop_all()
        db.create_all()

        admin = User('admin', admin=True)
        nobody = User('nobody')
        foobar = User('foobar')

        db.session.add(admin)
        db.session.add(foobar)
        db.session.add(nobody)
        db.session.commit()

        f1 = Flock(name='Jupyter and Drinks',
                   description="Let's chat about all things Jupyter",
                   where='front door',
                   when='7 pm',
                   leader=admin)

        f2 = Flock(name='the life of scipy',
                   description="Where are we going next?",
                   where='back door',
                   when='7 pm',
                   leader=nobody)

        db.session.add(f1)
        db.session.add(f2)
        db.session.commit()

        f1.birds.append(foobar)
        f1.birds.append(nobody)
        f2.birds.append(foobar)
        db.session.commit()

        db.session.add(Location('front door', 'http://placehold.it/350x150'))
        db.session.add(Location('back door', 'http://placehold.it/350x150'))
        db.session.add(Location('lobby', ''))
        db.session.commit()


@data.command()
def stress():
    """Drop / create tables, and seed 200 card test."""
    with app.app_context():
        click.confirm('Are you sure you want to reset {}?'.format(db.engine),
                      abort=True)
        db.drop_all()
        db.create_all()

        admin = User('admin', admin=True)
        db.session.add(admin)
        db.session.commit()

        for i in range(200):
            f = Flock(name='Flock {}'.format(i),
                      description='Description of flock {}'.format(i),
                      where='front door',
                      when='later tonight',
                      leader=admin)
            db.session.add(f)
        db.session.commit()

        db.session.add(Location('front door', 'http://placehold.it/350x150'))
        db.session.commit()


@data.command()
def empty():
    """Create empty database tables."""
    with app.app_context():
        click.confirm('Are you sure you want to create tables in {}?'.format(db.engine),
                      abort=True)
        db.create_all()


@data.command()
def reset():
    """Drop and create empty database tables."""
    with app.app_context():
        click.confirm('Are you sure you want to reset {}?'.format(db.engine),
                      abort=True)
        db.drop_all()
        db.create_all()


if __name__ == '__main__':
    admin()
