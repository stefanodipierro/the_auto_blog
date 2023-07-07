from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField
from wtforms.validators import DataRequired, NumberRange

class SearchForm(FlaskForm):
    """
    Form for users to search for a blog post.
    """
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Login form 
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')
# form for creator

class ContentCreationForm(FlaskForm):
    num_articles = IntegerField('Number of Articles', validators=[DataRequired(), NumberRange(min=1, message='Deve essere almeno 1')])
    topic = StringField('Topic', validators=[DataRequired()])
    submit = SubmitField('Generate')
    post_to_facebook = BooleanField('Post on Facebook')
    post_to_reddit = BooleanField('Post on Reddit')

class SocialMediaForm(FlaskForm):
    facebook = SubmitField('Add Facebook')
    reddit = SubmitField('Add Reddit')
