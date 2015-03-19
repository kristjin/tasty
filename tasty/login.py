__author__ = 'kristjin@github'
from flask.ext.login import LoginManager

from tasty import app
from .database import session
from .models import User

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login_get"
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(uid):
    return session.query(User).get(int(uid))