from gevent.pywsgi import WSGIServer
from database import app
from werkzeug.security import generate_password_hash
from schema import (ArticleSchema, UserSchema, UserArticleSchema)
from database import (db, User, Article, UsersArticles)
from flask import request, jsonify
from flask import abort
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
import base64
import datetime
import getpass

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
test_app = app.test_client()

user_schema = UserSchema()
users_schema = UserSchema(many=True)
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
user_article_schema = UserArticleSchema()
user_articles_schema = UserArticleSchema(many=True)
bcrypt = Bcrypt()


@auth.verify_password
def verify(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({"message": "UnauthorizedError"}, 401)
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "UnauthorizedError"}, 401)
    return True


@app.route('/user/login', methods=['GET'])
@auth.login_required()
def user_login():
    return jsonify(message="You are logged in", status=200)



#перевірка чи є залогінений юзер модератором
def chek_moderator():
    #curr_username = getpass.getuser() # =Настя
    curr_username = auth.current_user()
    user = User.query.filter_by(username=curr_username).first()
    if user.moderator == False:
        return jsonify(message="You are not moderator", status=200)
    return jsonify(message="You are moderator", status=200)


#створення юзера
#http://localhost:5000/user?username=nh&firstName=nastia&lastName=hudyma&email=nh@ex.com&password=password
@app.route('/user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        user_data = request.get_json()

        username = user_data.get('username')
        firstName = user_data.get('firstName')
        lastName = user_data.get('lastName')
        email = user_data.get('email')
        password = user_data.get('password')


        #hash_pwd = generate_password_hash(password)
        user = User.query.filter_by(username=username).first()
        try:
            UserSchema().load(user_data)
        except ValidationError:
            return jsonify({"message": "Error validation"}, 400)
        if user is not None:
            return jsonify({"message": "User with this username is already exist"}, 409)
        hash_password = bcrypt.generate_password_hash(password)

        new_user = User(username, firstName, lastName, email, hash_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify(UserSchema().dump(new_user))


#відображення всіх юзерів
#http://localhost:5000/users
@app.route('/users', methods=['GET'])
def users():
    all_users = User.query.all()
    if all_users is None:
        abort(404, description="Resource not found")
    result = users_schema.dump(all_users)
    return jsonify(result)


#відображення юзера
#http://localhost:5000/user/testuser
@app.route('/user/<username>', methods=['GET'])
def user_username(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({"message": "Resource not found"}, 404)
        return UserSchema().dump(user)


#редагування чи видалення юзера
#http://localhost:5000/user/testuser
@app.route('/user/<username>', methods=['PUT', 'DELETE'])
@auth.login_required()
def update_delete_user(username):
    if request.method == 'PUT':
        user_data = request.get_json()

        new_username = user_data.get('username')
        firstName = user_data.get('firstName')
        lastName = user_data.get('lastName')
        email = user_data.get('email')

        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({"message": "Resource not found"}, 404)

        try:
            UserSchema().load(user_data)
        except ValidationError:
            return jsonify({"message": "Error validation"}, 400)

        user.username = new_username
        user.firstName = firstName
        user.lastName = lastName
        user.email = email

        db.session.commit()
        return user_schema.jsonify(user)

    elif request.method == 'DELETE':
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({"message": "Resource not found"}, 404)
        db.session.delete(user)
        db.session.commit()

        return user_schema.jsonify(user)


#створення статті
#http://localhost:5000/article?title=NH article&text=my first article&author_id=4
@app.route('/article', methods=['POST'])
#@auth.login_required()
def create_article():
    if request.method == 'POST':
        article_data = request.get_json()

        title = article_data.get('title')
        text = article_data.get('text')
        author_id = article_data.get('author_id')

        try:
            ArticleSchema().load(article_data)
        except ValidationError:
            return jsonify({"message": "Error validation"}, 400)

        '''if not chek_moderator():
            curr_username = auth.current_user()
            user = User.query.filter_by(username=curr_username).first()
            user.moderator = True'''

        new_article = Article(title, text, author_id)

        db.session.add(new_article)
        db.session.commit()

        version = UsersArticles(text, author_id, author_id, new_article.article_ID)

        db.session.add(version)
        db.session.commit()

        return jsonify(ArticleSchema().dump(new_article))


#відображення конкретної статті з конкретною айдішкою
#http://localhost:5000/article/8
@app.route('/article/<int:id>', methods=['GET'])
def get_article_id(id):
    articles = Article.query.get(id)
    if articles is None:
        return jsonify({"message": "Resource not found"}, 404)
    return jsonify(ArticleSchema().dump(articles))


#зміна та видалення статті з конкретною айдішкою
#http://localhost:5000/article/9
@app.route('/article/<int:ids>', methods=['PUT', 'DELETE'])
@auth.login_required()
def update_delete_article(ids):
    if request.method == 'PUT':

        articles = Article.query.get(ids)
        if articles is None:
            return jsonify({"message": "Resource not found"}, 404)

        article_data = request.args
        text = article_data.get('text')
        user = article_data.get('editor')
        author = articles.user_ID

        # if not chek_moderator() or auth.current_user() != author:
        #    abort(403, description="You're not moderator")

        version = UsersArticles(text, user, author, articles.article_ID)

        db.session.add(version)
        db.session.commit()

        return article_schema.jsonify(articles)

    elif request.method == 'DELETE':
        articles = Article.query.get(ids)
        #author = articles.user_ID

        if articles is None:
            return jsonify({"message": "Resource not found"}, 404)

        '''if not chek_moderator() or auth.current_user() != author:
            abort(403, description="You're not moderator, you can't delete the article")'''

        db.session.delete(articles)
        db.session.commit()

        all_articles = Article.query.all()
        result = articles_schema.dump(all_articles)
        return jsonify(result)


@app.route('/user/moderator/<username>', methods=['GET', 'PUT'])
@auth.login_required()
def moderator(username):
    if request.method == 'GET':


        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({"message": "Resource not found"}, 404)
        article = Article.query.filter_by(user_ID=user.user_ID, status='wait for moderator').first()
        if article is None:
            return jsonify({"message": "Resource not found"}, 404)
        user_article = UsersArticles.query.filter_by(article_ID=article.article_ID, moderator_ID=user.user_ID).all()
        if user_article is None:
            return jsonify({"message": "Resource not found"}, 404)

        if user.moderator == False:
            return jsonify(message="You are not moderator", status=200)
        return jsonify(message="You are moderator", status=200)

        return jsonify(user_articles_schema.dump(user_article))

    elif request.method == 'PUT':


        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({"message": "Resource not found"}, 404)
        article_data = request.args
        article_id = article_data.get('article_ID')
        if user.moderator == False:
            return jsonify(message="You are not moderator", status=200)
        return jsonify(message="You are moderator", status=200)
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


#відображення всіх статей
#http://localhost:5000/blog
@app.route('/blog', methods=['GET'])
def blog():
    if request.method == 'GET':
        all_articles = Article.query.all()
        '''if all_articles is None:
            return jsonify({"message": "Resource not found"}, 404)'''
        result = articles_schema.dump(all_articles)
        return jsonify(result)


#відображення версій статей юзера
#http://localhost:5000/blog/user/nh1
@app.route('/blog/user/<username>', methods=['GET'])
#@auth.login_required()
def blog_username(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({"message": "Resource not found"}, 404)
        user_articles = UsersArticles.query.filter_by(moderator_ID=user.user_ID).all()
        if user_articles is None:
            abort(404, description="Resource not found")

        result = user_articles_schema.dump(user_articles)
        return jsonify(result)


#відображення версій конкретної статті
#http://localhost:5000/blog/user/3
@app.route('/blog/article/<int:ids>', methods=['GET'])
def blog_article(ids):
    if request.method == 'GET':
        articles = UsersArticles.query.filter_by(article_ID=ids).all()
        if articles is None:
            return jsonify({"message": "Resource not found"}, 404)
        result = user_articles_schema.dump(articles)
        return jsonify(result)


@app.route('/api/v1/hello-world-5')
@app.route('/')
def hello_world():
    return 'Hello World 5'

if __name__ == '__main__':
    app.run()


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
