from flask import Flask, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class User(db.Model):
    user_ID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    userStatus = db.Column(db.String, nullable=False)

    article = db.relationship("Article", backref="user")

class Article(db.Model):
    article_ID = db.Column(db.Integer, primary_key=True)
    user_ID = db.Column(db.Integer, db.ForeignKey(User.user_ID))
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    complete = db.Column(db.Boolean, nullable=False)

class UsersArticles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_ID = db.Column(db.Integer, db.ForeignKey(User.user_ID))
    article_ID = db.Column(db.Integer, db.ForeignKey(Article.article_ID))
    edited_text = db.Column(db.String)

if __name__ == '__main__':
    manager.run()

#u = User(username='Johnw', firstName='John', lastName='Yous', email='john@example.com', password='1111', userStatus='registered')