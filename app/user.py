import os
import sqlite3
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app import app

class User(UserMixin):
    def __init__(self, username, password_hash):
        self.username         = username
        self.password_hash    = password_hash

    @staticmethod
    def load(username):
        print('---DEBUG--- path to database:', os.path.join(app.config['DB_DIRECTORY'], 'users.db'))
        conn   = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'users.db'))
        cursor = conn.cursor()
        user   = cursor.execute('SELECT * FROM users WHERE username=?',
                (username,)).fetchone()
        
        if user is None:
            raise NameError(f"User '{username}' not found.")

        return User(user[0], user[1])

    def authenticate(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def __repr__(self):
        return f"User '{self.username}' (authenticated: {self.is_authenticated})"
