from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    """
    Form for users to search for a blog post.
    """
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')
