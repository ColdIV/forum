from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///../database/main.sqlt'
app.config['SECRET_KEY'] = 'example_key'
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
app.permanent_session_lifetime = timedelta(days=365)
Session(app)

# db will be initialized later
db = SQLAlchemy()

from app import views
# from app import database
