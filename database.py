from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class User(db.Model):
    __tablename__ = 'User'
    user_ID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    moderator = db.Column(db.Boolean, nullable=False)

    article = db.relationship('Article', backref='user', lazy='dynamic')

    def __init__(self, username, firstName, lastName, email, password):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.moderator = False


class Article(db.Model):
    __tablename__ = 'Article'
    article_ID = db.Column(db.Integer, primary_key=True)
    user_ID = db.Column(db.Integer, db.ForeignKey(User.user_ID))
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

    def __init__(self, title, text, user_ID):
        self.title = title
        self.text = text
        self.user_ID = user_ID
        self.status = 'complete'


class UsersArticles(db.Model):
    __tablename__ = 'UsersArticles'
    version_id = db.Column(db.Integer, primary_key=True)
    user_ID = db.Column(db.Integer, db.ForeignKey(User.user_ID))
    moderator_ID = db.Column(db.Integer, db.ForeignKey(User.user_ID))
    article_ID = db.Column(db.Integer, db.ForeignKey(Article.article_ID))
    edited_text = db.Column(db.String)
    edited_date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, text, user, moderator, article):
        self.edited_text = text
        self.user_ID = user
        self.moderator_ID = moderator
        self.article_ID = article



