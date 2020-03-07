#!/usr/bin/env python3

import os
import sqlite3
import sys

from datetime import datetime

from app import app
from app.hashing import id_from_filename
from app.logging import log

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        exit(1)
    else:
        file_id = id_from_filename(sys.argv[1])

        conn = sqlite3.connect(app.config['DB_FILE'])
        cursor = conn.cursor()
        cursor.execute('SELECT filename FROM files WHERE id=?', (file_id,))

        if cursor.fetchone() is not None:
            print('ERROR: A file with this file ID already exists in the database. Aborted.')
            conn.close()
            exit(1)

        choice = input(f'Do you want to add file {sys.argv[1]} with file ID "{file_id}"? (Y/n) ')
        choice = False if choice == 'n' else True

        if not choice:
            print('Aborted.')
            conn.close()
            exit(1)

        if not os.path.isfile(os.path.join(app.config['FILES_DIRECTORY'], sys.argv[1])):
            print(f'ERROR: No file named {sys.argv[1]} exists in {app.config["FILES_DIRECTORY"]}/.')
            print('Aborted.')
            conn.close()
            exit(1)

        time_uploaded = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        size = os.stat(os.path.join(app.config['FILES_DIRECTORY'], sys.argv[1])).st_size
        cursor.execute('INSERT INTO files VALUES(?, ?, ?, ?)', (file_id, sys.argv[1], time_uploaded, size))
        conn.commit()
        conn.close()

        log('terminal', 'terminal', 'upload', f'file_id: {file_id}, filename: {sys.argv[1]}')

        print(f'Added file {sys.argv[1]} to database. File ID: {file_id}')
