"""Data models for Flask Cafe"""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()


class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default="/static/images/default-cafe.jpg",
    )

    city = db.relationship("City", backref='cafes')

    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'

class User(db.Model):
    """User information."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    admin = db.Column(
        db.Boolean,
        nullable=False
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default='/static/images/default-pic.png'
    )

    hashed_password = db.Column(
        db.Text,
        nullable=False
    )

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def register(
        cls,
        username,
        email,
        first_name,
        last_name,
        description,
        password,
        image_url='/static/images/default-pic.png',
        admin=False):

        """Hashes password adds user to system."""

        hashed_password = bcrypt.generate_password_hash(
            password).decode('UTF-8')

        user = User(
            username=username,
            admin=admin,
            email=email,
            first_name=first_name,
            last_name=last_name,
            description=description,
            image_url=image_url,
            hashed_password=hashed_password
        )

        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'.

        Returns user instance if username is found and password is valid.

        Returns False if username is not found or password is invalid.
        """

        user = User.query.filter_by(username = username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.hashed_password, password)
            if is_auth:
                return user

        return False


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
