from flask_marshmallow import Marshmallow
from marshmallow import validate, fields
from flask_bcrypt import generate_password_hash
from database import app

ma = Marshmallow(app)


class ArticleSchema(ma.Schema):
    title = fields.String(required=True)
    text = fields.String(required=True)
    author_id = fields.Integer(required=False)


class UserSchema(ma.Schema):
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    username = fields.String(required=True)
    email = fields.String(required=True, validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)


class UserArticleSchema(ma.Schema):
    user_ID = fields.Integer(required=True)
    moderator_ID = fields.Integer(required=True)
    article_ID = fields.Integer(required=True)
    edited_text = fields.String(required=True)
    edited_date = fields.DateTime(required=True)

