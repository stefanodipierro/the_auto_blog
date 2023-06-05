# Import necessary modules from flask
from flask import render_template, request
from flask import jsonify
from . import bp  # Import the blueprint we created in __init__.py
from .models import Post, Image, User  # Import the Post model from the models module
from app import db
from .auth import auth


# Define the route for the homepage
@bp.route('/')
def home():
    """Renders the home page with all blog posts."""
    # Query all posts from the database
    posts = Post.query.all()

    # Pass the posts to the template
    return render_template('home.html', posts=posts)

# Define the route for the post detail page
@bp.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)  # This line fetches the post by id, or returns a 404 error if it doesn't exist.
    return render_template('post.html', post=post)


@bp.route('/search', methods=['GET', 'POST'])
def search():
    """
    Render search results page.
    """
    query = request.args.get('q', '')  # Get the search query from the query string
    # Perform the search in the database.
    # This is a placeholder and should be replaced with actual database query.
    results = Post.query.filter(Post.title.contains(query)).all()
    return render_template('search_results.html', query=query, results=results)

@bp.route('/load_more/<int:page>', methods=['GET'])
def load_more(page):
    """Endpoint to load more posts."""
    PER_PAGE = 10
    posts = Post.query.order_by(Post.date.desc()).paginate(page, PER_PAGE, False).items
    posts_json = [
        {
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'date': post.date.strftime('%B %d, %Y'),
            'images': [image.image_url for image in post.images]
        }
        for post in posts
    ]
    return jsonify(posts_json)


# Errors routes

@bp.app_errorhandler(404)
def not_found_error(error):
    """Render a custom 404 error page."""
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """Render a custom 500 error page."""
    db.session.rollback()  # rollback the session in case of database errors
    return render_template('500.html'), 500 

#API Endpoints

@bp.route('/api/posts', methods=['POST'])
@auth.login_required

def create_post():
    data = request.get_json() or {}
    post = Post()
    post.from_dict(data)
    db.session.add(post)
    db.session.commit()
    response = jsonify({"message": "Post created successfully", "id": post.id})
    response.status_code = 201
    return response

@bp.route('/api/posts', methods=['GET'])
@auth.login_required

def get_posts():
    """Retrieve all blog posts."""
    posts = Post.query.all()  # Query the database for all posts
    return jsonify([post.to_dict() for post in posts])  # Return the posts as a JSON array

# API to get 1 post only or delete, I had to merge the 2 endpoints for a 405 error

@bp.route('/api/posts/<int:post_id>', methods=['GET', 'DELETE'])
@auth.login_required

def handle_post(post_id):
    # Query the database for the post with the provided id
    post = Post.query.get_or_404(post_id)

    if request.method == 'GET':
        # Convert the Post object to a dict
        post_dict = post.to_dict()

        # Return the post details as JSON
        return jsonify(post_dict), 200

    elif request.method == 'DELETE':
        db.session.delete(post)
        db.session.commit()

        return jsonify({'message': 'Post deleted successfully'}), 200
    

# registration and login endpoints


@bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    token = user.generate_auth_token(3600)
    return jsonify({'token': token.decode('ascii'), 'duration': 3600}), 201

@bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        abort(400)    # invalid credentials
    token = user.generate_auth_token(3600)
    return jsonify({'token': token.decode('ascii'), 'duration': 3600}), 200









