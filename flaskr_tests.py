# -*- coding: utf-8 -*-
"""
    Flaskr Tests
    ~~~~~~~~~~~~
    Tests the Flaskr application.
    :copyright: (c) 2010 by Bashar Said.
"""
import os
import unittest
import tempfile
import app


class FlaskrTestCase(unittest.TestCase):  # pylint: disable=missing-docstring

    def setUp(self):
        """Before each test, set up a blank database"""
        self.db_fd, app.APP.config['DATABASE'] = tempfile.mkstemp()
        app.APP.config['TESTING'] = True
        self.app = app.APP.test_client()
        app.init_db()

    def tearDown(self):
        """Get rid of the database again after each test."""
        os.close(self.db_fd)
        os.unlink(app.APP.config['DATABASE'])

    def login(self, username, password):
        # pylint: disable=missing-docstring
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        # pylint: disable=missing-docstring
        return self.app.get('/logout', follow_redirects=True)

    # testing functions

    def test_empty_db(self):
        """Start with a blank database."""
        r_value = self.app.get('/')
        assert b'No entries here so far' in r_value.data

    def test_login_logout(self):
        """Make sure login and logout works"""
        r_value = self.login(app.APP.config['USERNAME'],
                             app.APP.config['PASSWORD'])
        assert b'You were logged in' in r_value.data
        r_value = self.logout()
        assert b'You were logged out' in r_value.data
        r_value = self.login(app.APP.config['USERNAME'] + 'x',
                             app.APP.config['PASSWORD'])
        assert b'Invalid username' in r_value.data
        r_value = self.login(app.APP.config['USERNAME'],
                             app.APP.config['PASSWORD'] + 'x')
        assert b'Invalid password' in r_value.data

    def test_messages(self):
        """Test that messages work"""
        self.login(app.APP.config['USERNAME'],
                   app.APP.config['PASSWORD'])
        r_value = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in r_value.data
        assert b'&lt;Hello&gt;' in r_value.data
        assert b'<strong>HTML</strong> allowed here' in r_value.data


if __name__ == '__main__':
    unittest.main()
