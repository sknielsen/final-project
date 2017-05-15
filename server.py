from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)
from model import User, Trip, Entry, Category, connect_to_db, db
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Required to use Flask sessions
# app.secret_key = os.environ['SECRET_KEY']
app.secret_key = 'abcde'

app.jinja_env.undefined = StrictUndefined
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Homepage."""
    if session.get('logged_in_user'):
        user_id = session['logged_in_user']
        user_trips = Trip.query.filter_by(user_id=user_id).all()
    else:
        user_trips = []

    return render_template("homepage.html", trips=user_trips)



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
            return redirect('/')

    except:
        flash("No user with that email")
        return redirect('/')


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

    category_id = request.args.get('filter')
    trip = Trip.query.get(trip_id)
    categories = Category.query.all()

    if category_id:
        entries = Entry.query.filter_by(trip_id=trip_id, type_id=category_id).all()
    else:
        entries = Entry.query.filter_by(trip_id=trip_id).all()

    return render_template('view_trip.html', entries=entries, trip=trip, categories=categories, filter_category=category_id)


@app.route('/add-entry/<trip_id>', methods=['POST'])
def add_entry(trip_id):
    """Add new trip from info in form"""

    name = request.form.get('name')
    address = request.form.get('address')
    notes = request.form.get('notes')
    category = request.form.get('category')

    entry = Entry(trip_id=trip_id, name=name, address=address, notes=notes,
                  type_id=category)


    db.session.add(entry)
    db.session.commit()
    # print entry.name
    if 'pic' in request.files:
        file = request.files['pic']
        if file and allowed_file(file.filename):
            # import pdb; pdb.set_trace()
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = str(trip_id) + '_' + str(entry.entry_id) + '.' + ext
            # filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    entry.photo_location = UPLOAD_FOLDER + filename
    db.session.commit()
    print entry.photo_location

    return redirect('/trip/%s/%s' % (trip_id, entry.entry_id))


@app.route('/trip/<trip_id>/<entry_id>')
def view_entry(trip_id, entry_id):
    """Show entry details"""

    entry = Entry.query.get(entry_id)

    return render_template('view_entry.html', entry=entry)


@app.route('/update-notes', methods=["POST"])
def update_notes():

    notes = request.form.get("notes")
    entry_id = request.form.get("entry")
    entry = Entry.query.get(entry_id)
    entry.notes = notes
    db.session.commit()

    return ""

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    connect_to_db(app)
    app.run(port=5000, host='0.0.0.0')
