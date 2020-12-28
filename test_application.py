import base64
import json
from copy import copy
import pytest
from flask import Flask
from flask_script import Manager
from database import User, db, Article, UsersArticles, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from app import auth, test_app
from schema import UserSchema


class data(object):
    user_data = {
        'username': 'mashkaN',
        'firstName': 'Mary',
        'lastName': 'Nyk',
        'email': 'mashs@ex.com',
        'password': 'password'}

    user_data_error = {
        'username': 'mashkaN',
        'firstName': 'Mary',
        'lastName': 'Nyk',
        'email': 'mas',
        'password': 'password'
    }

    '''user_data_edit = {
        'username': 'mashkaN',
        'firstName': 'Marya',
        'lastName': 'Nyko',
        'email': 'mashaa@ex.com',
    }'''

    article_data = {
        'title': 'Hello',
        'text': 'Hello world',
        'author_id': '9'
    }
    article_data_error = {
        'title': 'Hello',
        'text': 'Hello world',
        'author_id': '100'
    }


@pytest.fixture(name='client')
def initialize_authorized_test_client(monkeypatch):
    app.testing = True
    client = app.test_client()
    monkeypatch.setattr(auth, 'authenticate', lambda x, y: True)
    yield client
    app.testing = False


def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'Hello World 5' in rv.data

# http://localhost:5000/user?username=nh&firstName=nastia&lastName=hudyma&email=nh@ex.com&password=password
def test_create_user():
    data_user = copy(data.user_data)

    user_test = test_app.post('/user', json=data_user)
    global username_user
    username_user = User.query.filter_by(username=data.user_data['username']).first().username
    global id_user
    user = User.query.filter_by(username=data.user_data['username']).first()
    id_user = user.user_ID
    # global id_of_test_user
    # id_of_test_user = User.query.filter_by(login=data['login']).first().user_ID
    assert user_test.status_code == 200
    '''assert res.get_json() == {
        'message': "The user was created",
        'status': 200
    }'''



def test_create_user_exist():
    data_user = copy(data.user_data)
    user_test = test_app.post('/user', json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "User with this username is already exist"}, 409]


def test_create_user_validation_error():
    data_user = copy(data.user_data_error)
    user_test = test_app.post('/user', json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Error validation"}, 400]



    #assert res.get_json() == [{"message": "UnauthorizedError"}]



def test_login():
    cod = base64.b64encode(b'mashkaN:password').decode('utf-8')
    user_test = test_app.get('/user/login', headers={'Authorization': 'Basic ' + cod})
    assert user_test.status_code == 200


''''''''''''''''''''''''''''''


def test_users_list():
    all_users = User.query.all()


def test_edit_user_bad_id(client):
    data_user = copy(data.user_data)
    user_test = client.put('/user/aswf', json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_edit_user_validation_error(client):
    data_user = copy(data.user_data)
    data_user['firstName'] = None
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    user_test = client.put('/user/' + str(user.username), json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Error validation"}, 400]

def test_get_user(client):
    data_user = copy(data.user_data)
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    user_test = client.get('/user/' + str(user.username), json=data_user)
    assert user_test.status_code == 200

def test_get_user_error(client):
    data_user = copy(data.user_data)
    user_test = client.get('/user/aswf', json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_get_users(client):
    user_test = client.get('/users')
    assert user_test.status_code == 200


def test_edit_user(client):
    data_user = copy(data.user_data)
    data_user['firstName'] = 'Mashunya'
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    #res = client.delete("/user/" + str(user.username))
    # username_user = User.query.filter_by(username=data.user_data['username']).first()
    user_test = client.put('/user/' + str(user.username), json=data_user)
    assert user_test.status_code == 200

def test_moderators(client):
    data_user = copy(data.user_data)
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    article = Article.query.filter_by(user_ID=user.user_ID).first()
    user_test = client.get('/user/moderator/'+str(user.username), json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_create_acticle_validation_error():
    data_article = copy(data.article_data)
    data_article['title'] = None
    user_test = test_app.post('/article', json=data_article)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Error validation"}, 400]


def test_create_article():
    data_article = copy(data.article_data)
    global id_user
    # data.article_data['author_id'] = id_user
    user = User.query.filter_by(user_ID=id_user).first()
    user.moderator = True
    user_test = test_app.post('/article', json=data_article)
    global id_article
    article = Article.query.filter_by(user_ID=data.article_data['author_id']).first()
    id_article = article.article_ID
    assert user_test.status_code == 200

def test_get_article(client):
    data_article = copy(data.article_data)
    global id_article
    #user = User.query.filter_by(user_ID=id_user).first()
    user_test = client.get('/article/' + str(id_article), json=data_article)
    assert user_test.status_code == 200

def test_get_article_error(client):
    user_test = client.get('/article/10000')
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]


def test_edit_article_error(client):
    user_test = client.put('/article/10000')
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_edit_article(client):
    data_article = copy(data.article_data)
    data_article['title'] = 'Hello by me'
    global id_article
    user_test = client.put('/article/' + str(id_article), json=data_article)
    assert user_test.status_code == 200

def test_moderator_articles(client):
    data_user = copy(data.user_data)
    global id_user
    global id_article
    user = User.query.filter_by(user_ID=id_user).first()
    article = Article.query.filter_by(user_ID=user.user_ID).first()
    user_article = UsersArticles.query.filter_by(article_ID=article.article_ID, moderator_ID=user.user_ID).all()
    user_test = client.get('/user/moderator/'+str(user.username), json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_get_articles():
    user_test = test_app.get('/blog')
    assert user_test.status_code == 200

def test_get_article_user(client):
    data_article = copy(data.article_data)
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    user_test = client.get('/blog/user/' + str(user.username), json=data_article)
    assert user_test.status_code == 200

def test_get_article_user_error(client):
    data_article = copy(data.article_data)
    user_test = client.get('/blog/user/aswf', json=data_article)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_get_article_article(client):
    data_article = copy(data.article_data)
    global id_article
    articles = UsersArticles.query.filter_by(article_ID=id_article).all()
    user_test = client.get('/blog/user/' + str(id_article), json=data_article)
    assert user_test.status_code == 200

def test_get_article_article_error(client):
    data_article = copy(data.article_data)
    user_test = client.get('/blog/user/10000', json=data_article)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]


def test_moderator(client):
    data_user = copy(data.user_data)
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    user_test = client.get('/user/moderator/hkjk', json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_moderatorss(client):
    data_user = copy(data.user_data)
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    user_test = client.put('/user/moderator/hkjk', json=data_user)
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]



def test_delete_user_error(client):
    user_test = client.delete("/user/1000")
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_delete_user(client):
    global id_user
    user = User.query.filter_by(user_ID=id_user).first()
    user_test = client.delete("/user/" + str(user.username))
    assert user_test.status_code == 200
    '''assert res.get_json() == {
        'message': "The user was deleted",
        'status': 200
    }'''

def test_delete_article(client):
    global id_article
    #articles = Article.query.get(ids)
    #article = Article.query.filter_by(article_ID=id_article).first()
    user_test = client.delete("/article/" + str(id_article))
    assert user_test.status_code == 200

def test_delete_article_error(client):
    user_test = client.delete("/article/1000")
    assert user_test.status_code == 200
    assert user_test.get_json() == [{"message": "Resource not found"}, 404]

def test_clean():
    pass


'''DB.session.delete(Tag.query.filter_by(text=DATA.note_edit['new_tag']).first())
    DB.session.commit()'''
#coverage report --omit 'C:\Users\Маша\git\лаб9\new\enterp\*' -m
# coverage run -m --omit 'C:\Users\Маша\git\лаб9\new\enterp\*' pytest test_application.py
