#!/usr/bin/env python3
import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect('app/database/files.db')
    cursor = conn.cursor()
    for row in cursor.execute('SELECT * FROM files'):
        print(f'{row[0]}\t{row[1]}')
    conn.close()
