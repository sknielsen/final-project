from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash,
                   session)
from model import User, Trip, Entry, Category, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions
# app.secret_key = os.environ['SECRET_KEY']
app.secret_key = 'abcde'

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/create-account', methods=['GET'])
def create_account():
    """ Allows user to create a new account """
    return render_template('create_account.html')


@app.route('/create-account', methods=['POST'])
def check_create():
    """ Checks user email is new and processes registration """

    user_email = request.form.get('email')
    user_password = request.form.get('password')
    name = request.form.get('name')

    user = User.query.filter_by(email=user_email).all()

    if user:
        flash("User email already exists")
        return redirect('/login-form')
    else:
        new_user = User(email=user_email, password=user_password, name=name)
        db.session.add(new_user)
        db.session.commit()
        session['logged_in_email'] = user_email
        flash('You are now registered and logged in!')
        return redirect('/users/%s' % (user.user_id))


@app.route('/logout')
def logout():
    """Logs out user"""
    del session['logged_in_email']
    flash("You are now logged out.")
    return redirect('/')


@app.route('/login-form')
def login():
    """Prompts user to log in"""

    return render_template('login_form.html')


@app.route('/check-login', methods=['POST'])
def check_login():
    """Check if email in users table"""

    user_email = request.form.get('email')
    user_password = request.form.get('password')

    try:
        user = User.query.filter_by(email=user_email).one()
        if user.password == user_password:
            session['logged_in_email'] = user_email
            flash('Hello, %s' % (user.name))
            return redirect('/users/%s' % (user.user_id))
        else:
            flash('Wrong password!')
            return redirect('/login-form')

    except:
        flash("No user with that email")
        return redirect('/create-account')


@app.route('/users/<user_id>')
def user_profile(user_id):
    """Displays a user's profile """
    user = User.query.get(user_id)

    user_trips = user.trips
    # user_ratings = []
    # for rating in ratings:
    #     user_ratings.append((rating.movie.title, rating.score))

    # return render_template('user_profile.html', user_age=user_age, user_zip=user_zip,
                            # user_ratings=user_ratings)
    return render_template('user_profile.html', trips=user_trips)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    # app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)
    app.run(port=5000, host='0.0.0.0')
