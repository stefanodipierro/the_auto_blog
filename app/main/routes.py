# Import necessary modules from flask
from flask import render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import bp  # Import the blueprint we created in __init__.py
from .models import Post, Image, User  # Import the Post model from the models module
from .forms import RegistrationForm, LoginForm, ContentCreationForm, SocialMediaForm
from app import db
from .gpt4_service import generate_and_save_articles
import app.main.fb_script
from app import executor  # Import the executor directly
from flask import redirect
from facebook import GraphAPIError  # Questo è l'equivalente più vicino di FacebookResponseException nella libreria `facebook-sdk`

from facebook import GraphAPI  # Questo è l'equivalente più vicino di `facebook` nella libreria `facebook-sdk`
from requests import get
import urllib








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
@login_required

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
@login_required

def get_posts():
    """Retrieve all blog posts."""
    posts = Post.query.all()  # Query the database for all posts
    return jsonify([post.to_dict() for post in posts])  # Return the posts as a JSON array

# API to get 1 post only or delete, I had to merge the 2 endpoints for a 405 error

@bp.route('/api/posts/<int:post_id>', methods=['GET', 'DELETE'])
@login_required

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


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first() is not None:
            # existing user, you can flash a message here to let the user know
            # the username has been taken.
            return render_template('register.html', form=form)
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # redirect user to login page after successful registration.
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            # invalid credentials, you can flash a message here to let the user know
            flash('Invalid username or password', 'error') # Add this line to flash a message
            return render_template('login.html', form=form)
        login_user(user)
        return redirect(url_for('main.creator'))
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home')), 200


@bp.route('/creator', methods=['GET', 'POST'])
@login_required
def creator():
     
    social_form = SocialMediaForm()
   
    form = ContentCreationForm()
    # validation social form
    if social_form.validate_on_submit():
        if social_form.facebook.data:
            return redirect(url_for('main.connect_facebook'))
        elif social_form.reddit.data:
            # Reindirizza l'utente alla pagina di autorizzazione di Reddit
            pass  # Da implementare
        return redirect(url_for('main.creator'))  # Reindirizza l'utente alla stessa pagina del creatore
   
    #validation content generator form

    if form.validate_on_submit():
        num_articles = form.num_articles.data
        topic = form.topic.data
        post_to_facebook = form.post_to_facebook.data
        post_to_reddit = form.post_to_reddit.data
        
        # Avvia la generazione e il salvataggio degli articoli
        try:
            # Submit the task to the executor
            executor.submit(generate_and_save_articles, num_articles, topic, post_to_facebook, post_to_reddit)
            flash('Your articles are being generated.')
        except Exception as e:
            flash(f"Error: {str(e)}")
        return redirect(url_for('main.creator'))  # Reindirizza l'utente alla stessa pagina del creatore
    return render_template('creator.html', content_form=form, social_form=social_form)


# facebook 

@bp.route("/connect_facebook")
@login_required
def connect_facebook():
    # Creazione dell'URL di autorizzazione
    params = {
        "client_id": current_app.config['FACEBOOK_APP_ID'],
        "redirect_uri": url_for('main.facebook_callback', _external=True),  # Si assicura che l'URL sia assoluto
        "scope": "pages_read_engagement,pages_manage_posts",  # Impostare le autorizzazioni desiderate qui
        "state": "random_string"  # Si dovrebbe generare e salvare una stringa casuale per verificare la risposta
    }

    url = "https://www.facebook.com/dialog/oauth?" + urllib.parse.urlencode(params)
    return redirect(url)


@bp.route("/facebook_callback")
@login_required
def facebook_callback():
    code = request.args.get('code')
    state = request.args.get('state')

    # Si dovrebbe verificare la stringa di stato qui

    # Richiedere il token di accesso
    params = {
        "client_id": current_app.config['FACEBOOK_APP_ID'],
        "redirect_uri": url_for('main.facebook_callback', _external=True),  # Deve essere lo stesso di sopra
        "client_secret": current_app.config['FACEBOOK_APP_SECRET'],
        "code": code
    }

    url = "https://graph.facebook.com/v13.0/oauth/access_token?" + urllib.parse.urlencode(params)

    # Ottenere il token di accesso
    response = get(url)
    data = response.json()

    if 'access_token' in data:
        access_token = data['access_token']
        # Utilizzare access_token con GraphAPI e salvare nel database ecc.
    elif 'error' in data:
        # Gestire l'errore
        pass









