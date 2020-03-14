from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_nav import Nav, register_renderer

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

Bootstrap(app)
nav = Nav(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import navigation
from app import routes

register_renderer(app, 'bootstrap', navigation.BootstrapRenderer)