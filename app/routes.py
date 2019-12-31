import base64
import hashlib
import os
import sqlite3

from datetime import datetime
from flask import flash, url_for, redirect, render_template, request, send_from_directory
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from is_safe_url import is_safe_url
from urllib.parse import quote
from werkzeug.utils import secure_filename

from app import app, login_manager
from app.forms import LoginForm
from app.hashing import id_from_filename
from app.user import User
from app.logging import log

@app.errorhandler(404)
def not_found(error):
    return 'Invalid file id.', error.code

@app.route('/')
def index():
    return redirect(url_for('admin'))

@app.route('/by-name/<path:filename>')
def files_by_name(filename):
    file_id = id_from_filename(filename)
    return redirect(f'/{quote(file_id, safe="")}', 303)  # escape file_id

@app.route('/<path:file_id>')
def files(file_id):
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'files.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM files WHERE id=?', (file_id,))
    filename = cursor.fetchone()
    conn.close()

    if filename is not None:
        username = current_user.get_id() if current_user.is_authenticated else 'not_authenticated'
        log(username, 'download', f'ip: {request.remote_addr}, file_id: {file_id}, ' +
                f'filename: {filename[0]}')
        return send_from_directory(app.config['FILES_DIRECTORY'], filename[0],
                as_attachment=True)

    return 'Invalid file id.', 404

@app.route('/admin/')
def admin():
    return render_template('admin_base.html', title="Admin Overview")

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('admin'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.load(form.username.data)

            if not user.authenticate(form.password.data):
                raise ValueError('Invalid password.')

            login_user(user)
            flash('Successfully logged in.', 'success')
            log(user.get_id(), 'login', f'ip: {request.remote_addr}')

            next_addr = request.args.get('next')
            if not is_safe_url(next_addr, {request.host,}):
                return redirect(url_for('admin'))

            return redirect(next_addr or url_for('admin'))
        except (NameError, ValueError):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', title='Sign in', form=form)

@app.route('/admin/logout')
@login_required
def logout():
    log(current_user.get_id(), 'logout', f'ip: {request.remote_addr}')
    logout_user()
    flash('Successfully logged out.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/list')
@login_required
def list_files():
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'files.db'))
    cursor = conn.cursor()
    files = cursor.execute('SELECT * FROM files').fetchall()
    return render_template('list.html', title='List available files', file_list=files)

def allowed_file(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    return True

@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file_id = None

        if 'file' not in request.files:
            flash('Invalid upload.', 'danger')
            return redirect(url_for('upload'))

        f = request.files['file']
        if (f.filename == ''):
            flash('Invalid upload.', 'danger')
            return redirect(url_for('upload'))

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                flash('Invalid upload.', 'danger')
                return redirect(url_for('upload'))

            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            file_id = id_from_filename(filename)
            time_uploaded = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            size = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], filename)).st_size

            conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'files.db'))
            cursor = conn.cursor()
            cursor.execute('INSERT INTO files VALUES (?, ?, ?, ?)', (file_id, filename, time_uploaded, size))
            conn.commit()
            conn.close()
            
            flash('Successfully uploaded file.', 'success')
            log(current_user.get_id(), 'upload', f'ip: {request.remote_addr}, file_id: {file_id}, ' +
                    f'filename: {filename}')
        else:
            flash('Invalid upload.', 'danger')

        if file_id is not None:
            # escape file_id
            return render_template('upload.html', title='Upload file', file_id=quote(file_id, safe=''))
        else:
            return render_template('upload.html', title='Upload file')
    else:
        return render_template('upload.html', title='Upload file')

@app.route('/admin/delete/<path:file_id>')  # the path annotation is to match escaped slashes
@login_required
def delete(file_id):
    conn = sqlite3.connect(os.path.join(app.config['DB_DIRECTORY'], 'files.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM files WHERE id=?', (file_id,))

    res = cursor.fetchone()
    if res is not None:
        cursor.execute('DELETE FROM files WHERE id=?', (file_id,))
        conn.commit()
        os.remove(os.path.join(app.config['FILES_DIRECTORY'], res[0]))
        flash('Successfully deleted file.', 'success')
        log(current_user.get_id(), 'delete', f'ip: {request.remote_addr}, file_id: {file_id}, ' +
                    f'filename: {res[0]}')
    else:
        flash('Invalid id.', 'danger')

    conn.close()

    return redirect(url_for('list_files'))

@login_manager.user_loader
def load_user(username):
    return User.load(username)
