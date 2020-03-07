#!/usr/bin/env python3

import sqlite3

from app import app

if __name__ == '__main__':
    conn = sqlite3.connect(app.config['DB_FILE'])
    cursor = conn.cursor()
    for row in cursor.execute('SELECT * FROM files'):
        print(f'{row[0]}\t{row[1]}')
    conn.close()
