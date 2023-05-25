from app import create_app
from app.main.models import Post

app = create_app('testing')

if __name__ == '__main__':
    with app.app_context():
        posts = Post.query.all()
        print(f"There are {len(posts)} posts in the database.")
        for post in posts:
            print(post.title)
    app.run(debug=True)

