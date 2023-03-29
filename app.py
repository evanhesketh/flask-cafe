"""Flask App for Flask Cafe."""

import os

from flask import Flask, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Cafe, City

from forms import CafeForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")
app.config['SQLALCHEMY_ECHO'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global."""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None


# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.id


# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]


#######################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
    )


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
    )


@app.route('/cafes/add', methods=["GET", "POST"])
def handle_add_cafe():
    """If GET, shows add cafe form. If POST, handles form submission."""

    form = CafeForm()
    form.city_code.choices = CafeForm.get_city_choices()

    if form.validate_on_submit():
        cafe = Cafe(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            address=form.address.data,
            city_code=form.city_code.data,
            image_url=form.image_url.data or Cafe.image_url.default.arg
        )

        db.session.add(cafe)
        db.session.commit()

        flash(f"{cafe.name} added")

        return redirect(f'/cafes/{cafe.id}')

    else:
        return render_template('cafe/add-form.html', form=form)


@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def handle_edit_cafe(cafe_id):
    """If GET, shows edit cafe form. If POST, handles form submission."""

    cafe = Cafe.query.get_or_404(cafe_id)

    form = CafeForm(
        data={
            "name": cafe.name,
            "description": cafe.description,
            "url": cafe.url,
            "address": cafe.address,
            "city_code": cafe.city_code
        }
    )

    form.city_code.choices = CafeForm.get_city_choices()

    if form.validate_on_submit():
        cafe.name = form.name.data,
        cafe.description = form.description.data,
        cafe.url = form.url.data,
        cafe.address = form.address.data,
        cafe.city_code = form.city_code.data,
        cafe.image_url = form.image_url.data or Cafe.image_url.default.arg

        db.session.commit()

        flash(f"{cafe.name} edited")

        return redirect(f'/cafes/{cafe.id}')

    else:
        return render_template('cafe/edit-form.html', form=form, cafe=cafe)
