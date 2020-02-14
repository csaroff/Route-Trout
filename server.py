from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
import requests
import os

from model import User, Trail, User_Trail, db, connect_to_db

GOOGLE_MAPS_KEY = os.environ['GOOGLE_MAPS_KEY']
HIKING_PROJECT_KEY = os.environ['HIKING_PROJECT_KEY']

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

    # Form fields are not required - only update database if text was entered
    # in that field
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

    search_terms = request.args.get("search")
    api_url = "https://maps.googleapis.com/maps/api/geocode/json"
    payload = {
        "address": search_terms,
        "key": GOOGLE_MAPS_KEY
    }
    r = requests.get(api_url, params=payload)

    response = r.json()

    lat_long = response["results"][0]["geometry"]["location"]

    hiking_api_url = "https://www.hikingproject.com/data/get-trails"

    payload = {
        "lat": lat_long["lat"],
        "lon": lat_long["lng"],
        "key": HIKING_PROJECT_KEY
    }

    r2 = requests.get(hiking_api_url, params=payload)
    response2 = r2.json()

    trail_list = []

    for trail in response2["trails"]:
        trail_id = trail["id"]
        trail_name = trail["name"]
        length = trail["length"]
        difficulty = trail["difficulty"]
        img_thumb_url = trail["imgSmall"]
        img_lg_url = trail["imgSmallMed"]
        long = trail["longitude"]
        lat = trail["latitude"]
        location = trail["location"].split(",")
        city = location[0]
        state = location[1][1:]
        description = trail["summary"]

        if not Trail.query.filter_by(trail_id=trail_id).all():
            new_trail = Trail(trail_id=trail_id, trail_name=trail_name,
                              length=length, difficulty=difficulty,
                              img_thumb_url=img_thumb_url, img_lg_url=img_lg_url,
                              long=long, lat=lat, city=city, state=state, 
                              description=description)

            trail_list.append(new_trail)

            db.session.add(new_trail)
            db.session.commit()
        
        else:
            trail_list.append(Trail.query.get(trail_id))

    print(trail_list)

    return render_template("search.html", trail_list=trail_list)


@app.route("/trail/<int:trail_id>")
def display_trail_info():
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
