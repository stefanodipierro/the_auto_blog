from app import create_app
from app.main.models import Post

app = create_app('production')

if __name__ == '__main__':
    with app.app_context():
        posts = Post.query.all()

    app.run()

