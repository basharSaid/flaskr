# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~
    A microblog example application written as Flask tutorial with
    Flask and sqlite3.
    :copyright: (c) 2018 by Bashar Said.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

# create our little application
APP = Flask(__name__)

# Load default config and override config from an environment variable
APP.config.update(dict(
    DATABASE='/tmp/flaskr.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
APP.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    r_value = sqlite3.connect(APP.config['DATABASE'])
    r_value.row_factory = sqlite3.Row
    return r_value


def init_db():
    """Creates the database tables."""
    with APP.app_context():
        d_base = get_db()
        with APP.open_resource('schema.sql', mode='r') as file:
            d_base.cursor().executescript(file.read())
        d_base.commit()


def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    :return:
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@APP.teardown_appcontext
def close_db():
    """
    Closes the database again at the end of the request.
    :return:
    """
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@APP.route('/')
def show_entries():
    """
    :return:
    """
    d_base = get_db()
    cur = d_base.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@APP.route('/add', methods=['POST'])
def add_entry():
    """
    :return:
    """
    if not session.get('logged_in'):
        abort(401)
    d_base = get_db()
    d_base.execute('insert into entries (title, text) values (?, ?)',
                   [request.form['title'], request.form['text']])
    d_base.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@APP.route('/login', methods=['GET', 'POST'])
def login():
    """
    :return:
    """
    error = None
    if request.method == 'POST':
        if request.form['username'] != APP.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != APP.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@APP.route('/logout')
def logout():
    """
    :return:
    """
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@APP.route('/about')
def about():
    """
    :return:
    """
    return render_template('about.html')


if __name__ == '__main__':
    init_db()
    APP.run(debug=True, host='0.0.0.0', port=8080)
