from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, PasswordField
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

    @classmethod
    def get_city_choices(cls):
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

    password = PasswordField(
        "password",
        validators=[DataRequired(), Length(min=6)]
    )

    image_url = StringField(
        "image URL",
        validators=[Optional(), URL()]
    )

class ProfileEditForm(FlaskForm):
    """Form for editing user info."""

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

    password = PasswordField(
        "password",
        validators=[DataRequired()]
    )

class CSRFProtection(FlaskForm):
    """Form for CSRF protection."""

