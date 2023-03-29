from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL, Optional, Email, Length
from models import City
class CafeForm(FlaskForm):
    """Form for adding/editing cafes."""

    name = StringField(
        'Name',
        validators=[DataRequired()]
    )

    description = StringField(
        'Description',
        validators=[Optional()]
    )

    url = StringField(
        "URL",
        validators=[Optional(), URL()]
    )

    address = StringField(
        "Address",
        validators=[DataRequired()]
    )

    city_code = SelectField(
        "City",
        choices=[]
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL()]
    )

    #TODO: should this be a class method?
    def get_city_choices(self):
        """Get choices for city form field"""

        return [(c.code, c.name) for c in City.query.order_by('code')]

class SignupForm(FlaskForm):
    """Form for signing up new user."""

    username = StringField(
        "username",
        validators=[DataRequired()]
    )

    first_name = StringField(
        "first name",
        validators=[DataRequired()]
    )

    last_name= StringField(
        "last name",
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "description",
        validators=[Optional()]
    )

    email = StringField(
        "email",
        validators=[DataRequired(), Email()]
    )

    password = StringField(
        "password",
        validators=[DataRequired(), Length(min=6)]
    )

    image_url = StringField(
        "image URL",
        validators=[Optional(), URL()]
    )

class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField(
        "username",
        validators=[DataRequired()]
    )

    password = StringField(
        "password",
        validators=[DataRequired()]
    )
