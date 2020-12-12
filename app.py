from gevent.pywsgi import WSGIServer
from database import app
from schema import (ArticleSchema, UserSchema, UserArticleSchema)
from database import (db, User, Article, UsersArticles)
from flask import request, jsonify
from flask import abort
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt

user_schema = UserSchema()
users_schema = UserSchema(many=True)
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
user_article_schema = UserArticleSchema()
user_articles_schema = UserArticleSchema(many=True)
bcrypt = Bcrypt()


@app.errorhandler(404)
def error_404(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(400)
def error_400(e):
    return jsonify(error=str(e)), 400


@app.route('/article', methods=['POST', 'GET'])
def article():
    if request.method == 'POST':
        article_data = request.agrs
        title = article_data.get('title')
        text = article_data.get('text')
        author = article_data.get('author')

        try:
            ArticleSchema().load(article_data)
        except ValidationError:
            abort(400, description="Error validation")

        new_article = Article(title, text, author)

        db.session.add(new_article)
        db.session.commit()

        version = UsersArticles(text, author, author, new_article.article_ID)

        db.session.add(version)
        db.session.commit()

        return jsonify(ArticleSchema().dump(new_article))

    elif request.method == 'GET':
        all_articles = Article.query.all()
        if all_articles is None:
            abort(404, description="Resource not found")
        result = articles_schema.dump(all_articles)
        return jsonify(result)


@app.route('/article/<int:ids>', methods=['GET', 'PUT', 'DELETE'])
def article_id(ids):
    if request.method == 'GET':
        articles = Article.query.get(ids)
        if articles is None:
            abort(404, description="Resource not found")
        return jsonify(ArticleSchema().dump(articles))

    elif request.method == 'PUT':
        articles = Article.query.get(ids)
        if articles is None:
            abort(404, description="Resource not found")

        article_data = request.args
        text = article_data.get('text')
        user = article_data.get('editor')
        author = articles.user_ID

        if user == author:
            articles.text = text
            db.session.commit()
        else:
            articles.status = "wait for moderator"

        version = UsersArticles(text, user, author, articles.article_ID)

        db.session.add(version)
        db.session.commit()

        return article_schema.jsonify(articles)

    elif request.method == 'DELETE':
        articles = Article.query.get(ids)
        if articles is None:
            abort(404, description="Resource not found")
        db.session.delete(articles)
        db.session.commit()

        all_articles = Article.query.all()
        result = articles_schema.dump(all_articles)
        return jsonify(result)


@app.route('/user', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        user_data = request.args

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

    elif request.method == 'GET':
        all_users = User.query.all()
        if all_users is None:
            abort(404, description="Resource not found")
        result = users_schema.dump(all_users)
        return jsonify(result)


@app.route('/user/<username>', methods=['GET', 'PUT', 'DELETE'])
def user_username(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404, description="Resource not found")
        return UserSchema().dump(user)

    elif request.method == 'PUT':
        user_data = request.args
        new_username = user_data.get('username')
        firstName = user_data.get('firstName')
        lastName = user_data.get('lastName')
        email = user_data.get('email')

        user = User.query.filter_by(username=username).first()
        if user is None:
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

    elif request.method == 'DELETE':
        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404, description="Resource not found")
        db.session.delete(user)
        db.session.commit()

        return user_schema.jsonify(user)


@app.route('/user/moderator/<username>', methods=['GET', 'PUT'])
def moderator(username):
    if request.method == 'GET':
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


@app.route('/user/login', methods=['GET'])
def user_login():
    return 'Hello World 5'


@app.route('/user/logout', methods=['GET'])
def user_logout():
    return 'Hello World 5'


@app.route('/blog', methods=['GET'])
def blog():
    if request.method == 'GET':
        all_articles = Article.query.all()
        if all_articles is None:
            abort(404, description="Resource not found")
        result = articles_schema.dump(all_articles)
        return jsonify(result)


@app.route('/blog/user/<username>', methods=['GET'])
def blog_username(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(404, description="Resource not found")
        user_articles = UsersArticles.query.filter_by(moderator_ID=user.user_ID).all()
        if user_articles is None:
            abort(404, description="Resource not found")

        result = user_articles_schema.dump(user_articles)
        return jsonify(result)


@app.route('/blog/article/<int:ids>', methods=['GET'])
def blog_article(ids):
    if request.method == 'GET':
        articles = UsersArticles.query.filter_by(article_ID=ids).all()
        if articles is None:
            abort(404, description="Resource not found")

        result = user_articles_schema.dump(articles)
        return jsonify(result)


@app.route('/api/v1/hello-world-5')
@app.route('/')
def hello_world():
    return 'Hello World 5'


server = WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()
