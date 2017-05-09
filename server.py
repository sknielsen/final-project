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
    if session.get('logged_in_user'):
        user_id = session['logged_in_user']
        user_trips = Trip.query.filter_by(user_id=user_id).all()
    else:
        user_trips = []

    return render_template("homepage.html", trips=user_trips)


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
        user = User.query.filter_by(email=user_email).one()
        session['logged_in_user'] = user.user_id
        flash('Welcome, %s' % (user.name))
        return redirect('/')


@app.route('/logout')
def logout():
    """Logs out user"""
    del session['logged_in_user']
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
            session['logged_in_user'] = user.user_id
            flash('Hello, %s' % (user.name))
            return redirect('/')
        else:
            flash('Wrong password!')
            return redirect('/login-form')

    except:
        flash("No user with that email")
        return redirect('/create-account')


@app.route('/add-trip')
def new_trip():
    """Form that gets info for new trip"""

    return render_template('trip_form.html')


@app.route('/add-trip', methods=['POST'])
def add_trip():
    """Add new trip from info in form"""

    name = request.form.get('name')
    location = request.form.get('location')
    date = request.form.get('date')
    user_id = session['logged_in_user']

    trip = Trip(location=location, date=date, name=name, user_id=user_id)
    db.session.add(trip)
    db.session.commit()

    return redirect('/')

@app.route('/trip/<trip_id>')
def view_trip(trip_id):
    """Show entries for a trip"""

    entries = Entry.query.filter_by(trip_id=trip_id).all()

    return render_template('view_trip.html', entries=entries)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    connect_to_db(app)
    app.run(port=5000, host='0.0.0.0')
