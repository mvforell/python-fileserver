import os
import sqlite3

from sys import argv, exit

from app import app

if __name__ == '__main__':
    if len(argv) != 2:
        print(f'Usage: {argv[0]} <username>')
        exit(1)
    
    conn   = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'users.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username=?', (argv[1],))
    
    if cursor.fetchone() is None:
        print(f'No user named "{argv[1]}" exists.')
        exit(1)

    if not input(f'Do you really want to delete user "{argv[1]}"? (y/N) ').lower() == 'y':
        exit(1)

    cursor.execute('DELETE FROM users WHERE username=?', (argv[1],))
    conn.commit()
    conn.close()

    print(f'Successfully deleted user {argv[1]}.')
