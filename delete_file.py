#!/usr/bin/env python3

import os
import sqlite3
import sys

from app import app
from app.hashing import id_from_filename

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <filename>')
        exit(1)
    else:
        file_id = id_from_filename(sys.argv[1])

        conn = sqlite3.connect(app.config['DB_FILE'])
        cursor = conn.cursor()
        cursor.execute('SELECT filename FROM files WHERE id=?', (file_id,))

        if cursor.fetchone() is None:
            print('ERROR: No file with this file ID exists in the database. Aborted.')
            conn.close()
            exit(1)

        choice = input(f'Do you really want to delete file {sys.argv[1]} with file ID "{file_id}"? (Y/n) ')
        choice = False if choice == 'n' else True

        if not choice:
            print('Aborted.')
            conn.close()
            exit(1)

        cursor.execute('DELETE FROM files WHERE id=?', (file_id,))
        conn.commit()
        conn.close()

        os.remove(os.path.join('files', sys.argv[1]))

        print(f'Deleted file {sys.argv[1]} with file ID {file_id} from the database.')
