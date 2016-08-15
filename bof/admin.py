"""Admin control CLI."""
# Copyright (c) Peter Parente
# Distributed under the terms of the BSD 2-Clause License.
import click
from prettytable import PrettyTable
from . import app
from .model import db, User, Flock


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
@click.option('--id', prompt='Flock ID', type=int,
              help='Remove this flock ID.')
@click.confirmation_option(prompt='Are you sure you want to delete the flock?')
def remove(id):
    """Remove a flock."""
    with app.app_context():
        flock = Flock.query.get(id)
        db.session.delete(flock)
        db.session.commit()


@flock.command()
def edit():
    """Edit a flock."""
    pass

if __name__ == '__main__':
    admin()
