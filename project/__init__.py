from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
import os

app = Flask(__name__)

if os.environ.get('ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/warbler-db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or "it's a secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

modus = Modus(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from project.users.views import users_blueprint
from project.messages.views import messages_blueprint
from project.users.models import User, FollowersFollowee
from project.messages.models import Message

app.register_blueprint(users_blueprint, url_prefix='/users')
app.register_blueprint(
    messages_blueprint, url_prefix='/users/<int:id>/messages')


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def root():
    # current_user.following.all()
    # messages = Message.query.order_by("timestamp asc").limit(100).all()

    followees = User.query.get(current_user.id).following.all()
    followee_ids = [f.id for f in followees] + [current_user.id]

    # messages = Message.query.filter((Message.user_id.in_(
    #     followee_ids)).order_by("timestamp desc").limit(100).all())

    messages = Message.query.filter((Message.user_id.in_(followee_ids)) | (
        Message.user_id == current_user.id)).order_by("timestamp desc").limit(
        100).all()

    from IPython import embed
    embed()

    return render_template('home.html', messages=messages, current_user=current_user)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.errorhandler(404)
def page_not_found(e):

    return render_template('404.html'), 404
