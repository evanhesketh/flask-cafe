"""Flask App for Flask Cafe."""

import os

from flask import Flask, render_template, redirect, flash, session, g, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, Cafe, City, User

from forms import CafeForm, SignupForm, LoginForm, ProfileEditForm, CSRFProtection


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


@app.before_request
def add_csrf_from_to_g():

    g.csrf_form = CSRFProtection()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


#######################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html", form=g.csrf_form)


#######################################
# cafe routes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
        form=g.csrf_form
    )


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
        form=g.csrf_form
    )


@app.route('/cafes/add', methods=["GET", "POST"])
def handle_add_cafe():
    """If GET, shows add cafe form. If POST, handles form submission."""

    if not g.user or not g.user.admin:
        flash("You are not authorized to view that page", "danger")
        return redirect('/cafes')

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
        db.session.flush()

        cafe.save_map()
        
        db.session.commit()
    

        flash(f"{cafe.name} added")

        return redirect(f'/cafes/{cafe.id}')

    else:
        return render_template('cafe/add-form.html', form=form)


@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def handle_edit_cafe(cafe_id):
    """If GET, shows edit cafe form. If POST, handles form submission."""

    if not g.user or not g.user.admin:
        flash("You are not authorized to view that page", "danger")
        return redirect('/cafes')

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

###########################################################################
# user routes


@app.route('/signup', methods=["GET", "POST"])
def handle_signup():
    """If GET, display signup form.

    If POST, signup user and redirect to list of cafes.

    If username or email already exists in database, flash a message to user
    and present signup form again.

    """

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                description=form.description.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                password=form.password.data
            )
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash('username and/or email already taken', 'danger')

            return render_template('auth/signup-form.html', form=form)

        do_login(user)

        flash("You are signed up and logged in", 'success')
        return redirect('/cafes')

    else:
        return render_template('auth/signup-form.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def handle_login():
    """If GET, display login form."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username=form.username.data,
            password=form.password.data
        )

        if user:
            do_login(user)

            flash(f"Hello, {user.username}!", "success")
            return redirect('/cafes')

        else:
            flash("Invalid username and/or password", "danger")

    return render_template('auth/login-form.html', form=form)


@app.post('/logout')
def handle_logout():
    """Logs out current user and removes user id from session.
    Redirects to hompage.
    """

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')

    do_logout()

    flash("You have successfully logged out", "success")
    return redirect('/')


@app.get('/profile')
def show_user_profile():
    """Show user profile page."""

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect('/login')

    user = g.user

    return render_template('profile/detail.html', user=user, form=g.csrf_form)


@app.route('/profile/edit', methods=["GET", "POST"])
def handle_edit_profile():
    """If GET, display edit profile form.
    IF POST, update db with entered information.

    Redirect to profile page with flashed message, "Profile edited."
    """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect('/login')

    user = User.query.get_or_404(g.user.id)
    form = ProfileEditForm(
        data={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "description": user.description,
            "email": user.email
        }
    )

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.description = form.description.data
        user.email = form.email.data
        user.image_url = form.image_url.data or User.image_url.default.arg

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            flash("Email already taken", "danger")
            return render_template('profile/edit-form.html', form=form)

        flash("Profile edited", "success")
        return redirect('/profile')

    else:
        return render_template('profile/edit-form.html', form=form)

###############################################################################
# like routes


@app.get('/api/likes')
def handle_like_query():
    if not g.user:
        error_msg = {"error": "Not logged in"}
        return jsonify(error_msg)

    cafe_id = int(request.args['cafe_id'])

    for cafe in g.user.liked_cafes:

        if cafe.id == cafe_id:
            return jsonify({"likes": True})

    return jsonify({"likes": False})


@app.post('/api/like')
def handle_like_cafe():
    if not g.user:
        error_msg = {"error": "Not logged in"}
        return jsonify(error_msg)

    cafe_id = int(request.json['cafe_id'])

    cafe = Cafe.query.get(cafe_id)
    g.user.liked_cafes.append(cafe)

    db.session.commit()

    return jsonify(liked=cafe.id)


@app.post('/api/unlike')
def handle_unlike_cafe():
    if not g.user:
        error_msg = {"error": "Not logged in"}
        return jsonify(error_msg)

    cafe_id = int(request.json['cafe_id'])

    cafe = Cafe.query.get(cafe_id)
    g.user.liked_cafes.remove(cafe)

    db.session.commit()

    return jsonify(unliked=cafe.id)
