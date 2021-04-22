from gevent.pywsgi import WSGIServer
from database import app
from schema import (ArticleSchema, UserSchema, UserArticleSchema)
from database import (db, User, Article, UsersArticles)
from flask import request, jsonify
from flask import abort
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import base64
import datetime
import getpass

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
cors = CORS(app)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
user_article_schema = UserArticleSchema()
user_articles_schema = UserArticleSchema(many=True)
bcrypt = Bcrypt()


# перевірка чи є залогінений юзер модератором
def chek_moderator():
    # curr_username = getpass.getuser() # =Настя
    curr_username = auth.current_user()
    user = User.query.filter_by(username=curr_username).first()
    if user.moderator == False:
        return False
    return True


@auth.verify_password
def verify(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(401, description="UnauthorizedError")
    if not bcrypt.check_password_hash(user.password, password):
        abort(401, description="UnauthorizedError")
    return True


# WORK
# логування юзера
# http://localhost:5000/login
@app.route('/login', methods=['GET'])
@auth.login_required()
def user_login():
    return jsonify(message="You are logged in", status=200)


# WORK
# створення юзера
# http://localhost:5000/register?username=nh&firstName=nastia&lastName=hudyma&email=nh@ex.com&password=password
@app.route('/register', methods=['POST'])
def create_user():
    if request.method == 'POST':
        user_data = request.get_json()

        username = user_data.get('username')
        firstName = user_data.get('firstName')
        lastName = user_data.get('lastName')
        email = user_data.get('email')
        password = user_data.get('password')
        hash_password = bcrypt.generate_password_hash(password)

        try:
            UserSchema().load(user_data)
        except ValidationError:
            abort(400, description="Error validation")

        new_user = User(username, firstName, lastName, email, hash_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify(UserSchema().dump(new_user))


# WORK
# відображення всіх юзерів
# http://localhost:5000/users
@app.route('/users', methods=['GET'])
def users():
    all_users = User.query.all()
    if all_users is None:
        abort(404, description="Resource not found")
    result = users_schema.dump(all_users)
    return jsonify(result)


# WORK
# відображення юзера
# http://localhost:5000/user/testuser
@app.route('/user/<username>', methods=['GET'])
def user_username(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404, description="Resource not found")
        return UserSchema().dump(user)


# WORK
# редагування юзера
# http://localhost:5000/user/edit/ah1?username=ah2&firstName=nastia&lastName=hudyma&email=ah2@gmail.com
@app.route('/user/edit/<username>', methods=['PUT'])
@auth.login_required()
def update_user(username):
    if request.method == 'PUT':
        user_data = request.args
        new_username = user_data.get('username')
        firstName = user_data.get('firstName')
        lastName = user_data.get('lastName')
        email = user_data.get('email')

        user = User.query.filter_by(username=username).first()
        if user is None or user.username != auth.current_user():
            abort(404, description="Resource not found")

        try:
            UserSchema().load(user_data)
        except ValidationError:
            abort(400, description="Error validation")

        user.username = new_username
        user.firstName = firstName
        user.lastName = lastName
        user.email = email

        db.session.commit()
        return user_schema.jsonify(user)


# WORK
# видалення юзера
# http://localhost:5000/user/delete/ah1
@app.route('/user/delete/<username>', methods=['DELETE'])
@auth.login_required()
def delete_user(username):
    if request.method == 'DELETE':
        user = User.query.filter_by(username=username).first()
        if user is None or user.username != auth.current_user():
            abort(404, description="Resource not found")
        db.session.delete(user)
        db.session.commit()

        return user_schema.jsonify(user)


# WORK
# створення статті
# http://localhost:5000/article/create?title=NH article&text=my first article
@app.route('/article/create', methods=['POST'])
# @auth.login_required()
def create_article():
    if request.method == 'POST':
        article_data = request.get_json()
        title = article_data.get('title')
        text = article_data.get('text')

        curr_username = auth.current_user()
        user = User.query.filter_by(username=curr_username).first()
        # author_id = user.user_ID
        author_id = 9

        try:
            ArticleSchema().load(article_data)
        except ValidationError:
            abort(400, description="Error validation")

        # if not chek_moderator():
        #     curr_username = auth.current_user()
        #     user = User.query.filter_by(username=curr_username).first()
        #     user.moderator = True

        new_article = Article(title, text, author_id)

        db.session.add(new_article)
        db.session.commit()

        version = UsersArticles(text, author_id, author_id, new_article.article_ID)

        db.session.add(version)
        db.session.commit()

        return jsonify(ArticleSchema().dump(new_article))


# WORK
# відображення конкретної статті з конкретною айдішкою
# http://localhost:5000/article/8
@app.route('/article/<int:id>', methods=['GET'])
def get_article_id(id):
    articles = Article.query.get(id)
    if articles is None:
        abort(404, description="Resource not found")
    return jsonify(ArticleSchema().dump(articles))


# WORK
# зміна статті з конкретною айдішкою
# http://localhost:5000/article/edit/11?title=new title&text=new text
@app.route('/article/edit/<int:ids>', methods=['PUT'])
@auth.login_required()
def update_article(ids):
    if request.method == 'PUT':

        article = Article.query.get(ids)
        if article is None:
            abort(404, description="Resource not found")

        article_data = request.args
        title = article_data.get('title')
        text = article_data.get('text')
        # user = article_data.get('editor')
        author = article.user_ID

        curr_user = User.query.filter_by(user_ID=author).first()
        if not chek_moderator() or auth.current_user() != curr_user.username:
            abort(403, description="You're not moderator")

        article.title = title
        article.text = text

        db.session.commit()
        return article_schema.jsonify(article)


# WORK
# видалення статті з конкретною айдішкою
# http://localhost:5000/article/delete/11
@app.route('/article/delete/<int:ids>', methods=['DELETE'])
@auth.login_required()
def delete_article(ids):
    if request.method == 'DELETE':
        articles = Article.query.get(ids)
        author = articles.user_ID

        if articles is None:
            abort(404, description="Resource not found")

        curr_user = User.query.filter_by(user_ID=author).first()
        if not chek_moderator() or auth.current_user() != curr_user.username:
            abort(403, description="You're not moderator, you can't delete the article")

        db.session.delete(articles)
        db.session.commit()

        all_articles = Article.query.all()
        result = articles_schema.dump(all_articles)
        return jsonify(result)


# WORK
# відображення всіх статей
# http://localhost:5000/home
@app.route('/home', methods=['GET'])
def blog():
    if request.method == 'GET':
        all_articles = Article.query.all()
        if all_articles is None:
            abort(404, description="Resource not found")
        result = articles_schema.dump(all_articles)
        return jsonify(result)


# WORK
# відображення статей юзера
# http://localhost:5000/blog/ah
@app.route('/blog/<username>', methods=['GET'])
def blog_username(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404, description="Resource not found")
        user_articles = Article.query.filter_by(user_ID=user.user_ID).all()
        if user_articles is None:
            abort(404, description="Resource not found")

        result = articles_schema.dump(user_articles)
        return jsonify(result)


@app.route('/api/v1/hello-world-5')
@app.route('/')
def hello_world():
    return 'Hello World 5'


#відображення версій конкретної статті
#http://localhost:5000/blog/user/3
@app.route('/blog/article/<int:ids>', methods=['GET'])
def blog_article(ids):
    if request.method == 'GET':
        articles = UsersArticles.query.filter_by(article_ID=ids).all()
        if articles is None:
            abort(404, description="Resource not found")

        result = user_articles_schema.dump(articles)
        return jsonify(result)


@app.route('/user/moderator/<username>', methods=['GET', 'PUT'])
@auth.login_required()
def moderator(username):
    if request.method == 'GET':
        if not chek_moderator():
            abort(403, description="You're not moderator")

        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404, description="Resource not found")
        article = Article.query.filter_by(user_ID=user.user_ID, status='wait for moderator').first()
        if article is None:
            abort(404, description="Resource not found")
        user_article = UsersArticles.query.filter_by(article_ID=article.article_ID, moderator_ID=user.user_ID).all()
        if user_article is None:
            abort(404, description="Resource not found")
        return jsonify(user_articles_schema.dump(user_article))

    elif request.method == 'PUT':
        if not chek_moderator():
            abort(403, description="You're not moderator")

        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404, description="Resource not found")
        article_data = request.args
        article_id = article_data.get('article_ID')
        changes = article_data.get('changes')
        if changes == 'yes' or changes == 'YES' or changes == 'Yes' or changes == 1:
            article = Article.query.filter_by(article_ID=article_id, status='wait for moderator').first()
            if article is None:
                abort(404, description="Resource not found")
            user_article = UsersArticles.query.filter_by(article_ID=article_id, moderator_ID=user.user_ID).all()
            if user_article is None:
                abort(404, description="Resource not found")
            for usr in user_article:
                last = usr
            article.text = last.edited_text
            article.status = 'complete'
            db.session.commit()
        else:
            article = Article.query.filter_by(article_ID=article_id, status='wait for moderator').first()
            article.status = 'complete'
            db.session.commit()
        return jsonify(article_schema.dump(article))


server = WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()

'''#відображення всіх статей
#http://localhost:5000/articles
@app.route('/articles', methods=['GET'])
def get_article():
    all_articles = Article.query.all()
    if all_articles is None:
        abort(404, description="Resource not found")
    result = articles_schema.dump(all_articles)
    return jsonify(result)'''

'''@app.errorhandler(404)
def error_404(e):
    return jsonify(error=str(e)), 404
@app.errorhandler(400)
def error_400(e):
    return jsonify(error=str(e)), 400'''
