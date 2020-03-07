# python-fileserver
A simple fileserver written in Python using `flask`.

## Capabilities
This server provides a simple self-hosted way to upload and re-download files. Registered admins can upload new files and manage available ones.
The server computes a hash of a given file name and truncates it to length eight (called the file id) to enable short links (to change the algorithm, see the Configuration section).

Usage is as follows:
* to download a file, use either `GET /<file id>` or `GET /by-name/<file name>`.
* to open the admin section, use either `GET /` or `GET /admin/`.
* to upload new files or manage (list/delete) already available files, use the admin section.

## Dependencies and installation
This fileserver requires `python >= 3.6` and `uwsgi` with the `python3` plugin. (__Note:__ depending on your OS the plugin might be named `python` instead; if this is the case you also need to change the relevant section in your `uwsgi.ini`.)

To install it, clone this repository to the directory you want the server to run from. Then create a virtual environment, e.g. with `python3 -m venv venv`, activate it with `source venv/bin/activate` and run `pip install -r requirements.txt`.

The `sqlite3` database uses the following tables:
* `CREATE TABLE users (username text, password_hash text)`
* `CREATE TABLE files (id text, filename text, uploaded datetime, size integer)`
* `CREATE TABLE logs (timestamp INTEGER, user TEXT, ip_address TEXT, action TEXT, info TEXT)`

## Configuration
To configure the fileserver itself, edit `app/config.py.example` and save it to `app/config.py` (for information on the `SECRET_KEY` option, see part III of the Flask Mega-Tutorial linked below). To change `uwsgi` deployment settings, edit `uwsgi.ini.example` and save it to `uwsgi.ini`.

I personally use `systemd` to manage the `uwsgi` instance running the server and `nginx` to serve it to the internet. A `.service` file for the `uwsgi` service could look like this:
```
[Unit]
Description=uWSGI running a custom Flask file server

[Service]
Type=simple
PIDFile=/run/uwsgi-fileserver.pid
ExecStart=/usr/bin/uwsgi uwsgi.ini
User=http
Group=http
WorkingDirectory=...
Restart=on-failure
RestartSec=10
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target
```
And the relevant section in your nginx config like this:
```
server {
        server_name ...;

        location / {
                include uwsgi_params;
                uwsgi_pass 127.0.0.1:3031;
        }

        location /admin/upload {
                client_max_body_size 256M;
                include uwsgi_params;
                uwsgi_pass 127.0.0.1:3031;
        }

        ...
}
```
Make sure that the port for the `uwsgi_pass` section in your `nginx` config matches the one specified in `uwsgi.ini`.

To change the algorithm used for computing the `file_id` from a given file name, edit `id_from_filename()` in `app/hashing.py`.

This server is meant to be served at the root of a (sub)domain. It is possible to change that, though it will require a lot of editing of the source code (mostly in `app/routes.py` and `app/templates/*.html`, but I'm not sure whether that's all).

## User management and manual upload/deletion of files
For user management (adding/deleting users) and manually (using the console of your server) uploading or deleting files please use the provided scripts. (__Note:__ they need to be run from the installed virtualenv, because they use the configuration from the `app` package which in turn imports `flask` etc.)

## Privacy notes
This server keeps logs in a database. These logs include the username (if logged in), the client IP address, the performed action (login/logout/upload/download/delete) and additional information like the file id or file name. For privacy reasons these logs should be anonymized (redact username and IP addresses) regularly (e.g. anonymize logs older than 30 days every day). `anonymize_logs.sh` does exactly that (the required age for anonymization can easily be changed in the script) using `anonymize_logs_older_than(days=30)` in `app/logging.py`. I recommend setting up a `systemd` service and timer unit to call that script daily. The `.service` and `.timer` files respectively could look like this:
```
[Unit]
Description=Anonymize the logs of the python fileserver

[Service]
Type=oneshot
ExecStart=.../anonymize_logs.sh
User=http
Group=http
WorkingDirectory=...
```
```
[Unit]
Description=Anonymize the fileserver logs daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

## Additional notes
* The server uses `werkzeug`'s `generate_password_hash()` and `check_password_hash()` functions for storing and checking passwords. For further information see the `werkzeug` [documentation]( https://werkzeug.palletsprojects.com).
* This project largely benefitted from Miguel Grinberg's [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world), which I can only recommend to anyone wanting to get into web development using `flask`.
