from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
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
