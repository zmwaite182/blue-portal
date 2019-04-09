import os
import psycopg2

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        # open a connection, save it to close when done
        DB_URL = os.environ.get('DATABASE_URL', None)
        if DB_URL:
            g.db = psycopg2.connect(DB_URL, sslmode='require')
        else:
            g.db = psycopg2.connect(
                f"dbname={current_app.config['DB_NAME']}" +
                f" user={current_app.config['DB_USER']}"
            )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close() # close the connection


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        cur = db.cursor()
        cur.execute(f.read())
        cur.close()
        db.commit()

def add_user(email, password, role):
    db = get_db()
    db.execute('INSERT INTO user (email, password, role) VALUES (%s, %s, %s)', (email, generate_password_hash(password), role))
    db.commit()
    db.close()



@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('add-user')
@with_appcontext
def add_user_command():
    """Clear the existing data and create new tables."""
    init_db()
    cont = True
    num = 0
    click.echo('Begin adding users')
    while cont == True:
        print('Email?')
        email = input('> ')
        print('Password?')
        password = input('> ')
        print('Role?')
        role = input('> ')
        add_user(email, password, role)
        num += 1
        print('Would you like to continue?')
        answer = input('> ')
        if answer != 'y':
            cont = False
    click.echo(f'Added {num} users')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_user_command)
