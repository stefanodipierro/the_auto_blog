from app import db
from datetime import datetime



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

