from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

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
