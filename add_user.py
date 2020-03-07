#!/usr/bin/env python3

import sqlite3

from getpass import getpass
from werkzeug.security import generate_password_hash
from sys import exit

from app import app

if __name__ == '__main__':
    username = input('Enter username: ')
    password = getpass('Enter password: ')
    
    if not password == getpass('Re-enter password: '):
        print('Passwords do not match.')
        exit(1)

    password_hash = generate_password_hash(password)
    conn = sqlite3.connect(app.config['DB_FILE'])
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users VALUES (?, ?)', (username, password_hash))
    conn.commit()
    conn.close()

    print(f'Successfully added user {username}.')
