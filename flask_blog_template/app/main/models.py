from app import db
from flask import current_app
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.jose import jwt

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    images = db.relationship('Image', backref='post', lazy=True)

    def from_dict(self, data):
        for field in ['title', 'description', 'date']:
            if field in data:
                setattr(self, field, data[field])
        if 'images' in data:
            for url in data['images']:
                self.images.append(Image(image_url=url))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'images': [image.image_url for image in self.images]
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        header = {"alg": "HS256"}
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=expiration),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        s = jwt.encode(header, payload, current_app.config['SECRET_KEY'])
        return s

    @staticmethod
    def verify_auth_token(token):
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'])
            user_id = payload['sub']
        except (jwt.ExpiredTokenError, jwt.InvalidTokenError):
            return None
        user = User.query.get(user_id)
        return user
