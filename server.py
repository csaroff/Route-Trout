from flask import (Flask, render_template, redirect, request, flash, session)
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Trail, User_Trail, db, connect_to_db

app = Flask(__name__)

app.secret_key = "supersecret"

# For getting error messages in Jinja when variables are undefined
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Display homepage"""

    return render_template("index.html")


@app.route("/register")
def reg_form():
    """Display registration form"""

    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_user():
    """Creates new user if user does not yet exist"""

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")


# Validate if username or email already exists in the users table in database
    if not User.query.filter((User.email == email) | (User.username == username)).all():

        user = User(username=username, email=email, password=password)

        db.session.add(user)
        db.session.commit()

        flash("User created!")

        return redirect("/login")

# If one does exist, flash message to indicate if email or username
    else:
        if User.query.filter_by(email=email).all():
            flash(f"There's already an account associated with {email}")
        else:
            flash(f"The username {username} is already taken")

        return redirect("/register")


@app.route("/login")
def show_login_form():
    """Display login form"""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def log_in_user():
    """Validate user login"""

    username = request.form.get("username")
    password = request.form.get("password")

    # Validate that user's username and password match database
    if User.query.filter((User.username == username) & (User.password == password)).all():
        session["username"] = username
        flash("Login successful")

        return redirect("/")

    else:
        flash("Incorrect login information")
        return redirect("/login")


@app.route("/account")
def show_account_options():
    """Display account options for logged in users"""

    return render_template("account.html")


@app.route("/account", methods=["POST"])
def update_account_info():
    """Update a user's account information"""

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    cell = request.form.get("cell")
    city = request.form.get("city")
    state = request.form.get("state")
    zipcode = request.form.get("zipcode")

    user = User.query.filter_by(username=session["username"]).first()

    if len(fname) > 0:
        user.fname = fname

    if len(lname) > 0:
        user.lname = lname

    if len(cell) > 0:
        user.cell = cell

    if len(city) > 0:
        user.city = city

    if len(state) > 0:
        user.state = state

    if len(zipcode) > 0:
        user.zipcode = zipcode

    db.session.add(user)
    db.session.commit()

    flash("Information updated!")

    return redirect("/account")


@app.route("/logout")
def log_out_user():
    """Log out user"""

    del session["username"]
    flash("Logged out")

    return redirect("/")


@app.route("/search")
def search_for_trails():
    """Something goes here"""

    return


@app.route("/trail/<int:trail_id>")
def display_trail_info(trail_id):
    """Display trail information page"""

    return render_template("trail.html", trail_id=trail_id)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
