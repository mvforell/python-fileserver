import os
import sqlite3

from datetime import datetime, timedelta

from app import app

def get_current_timestamp():
    return int(datetime.now().timestamp() * 1000)

def get_datetime_from_timestamp(ts):
    return datetime.fromtimestamp(ts / 1000)

def create_table():
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'logs.db'))
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE logs (timestamp INTEGER, user TEXT, ip_address TEXT, ' +
            'action TEXT, info TEXT)')
    conn.commit()
    conn.close()

def clear_logs():
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'logs.db'))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM logs')
    conn.commit()
    cursor.execute('VACUUM')
    conn.commit()
    conn.close()

def log(user, ip_address, action, info):
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'logs.db'))
    cursor = conn.cursor()
    cursor.execute('INSERT INTO logs VALUES (?, ?, ?, ?, ?)',
            (get_current_timestamp(), user, ip_address, action, info))
    conn.commit()
    conn.close()

def get_last_logs(count=1000, timestamps=False):
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'logs.db'))
    cursor = conn.cursor()
    results = cursor.execute('SELECT timestamp, user, ip_address, action, info FROM logs').fetchmany(count)
    conn.close()
    
    for res in results:
        timestamp, *rest = res
        if timestamps:
            timestamp /= 1000
        else:
            timestamp = get_datetime_from_timestamp(timestamp).strftime('%Y-%d-%m %H:%M:%S')
        yield [timestamp] + rest

def anonymize_logs_older_than(days=30):
    ts_n_days_ago = (datetime.now() - timedelta(days=days)).timestamp() * 1000
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'logs.db'))
    cursor = conn.cursor()
    cursor.execute("UPDATE logs SET user = 'anonymized', ip_address = 'anonymized' " +
            "WHERE timestamp < ? AND user != 'anonymized'", (ts_n_days_ago,))
    conn.commit()
    conn.close()
