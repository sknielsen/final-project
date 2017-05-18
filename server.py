from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)
from model import User, Trip, Entry, Category, Share, connect_to_db, db
import os
from werkzeug.utils import secure_filename
import bcrypt

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

def has_access(trip_id):
    """Determine wither the user that is logged in can view the trip or not"""

    if not session.get('logged_in_user'):
        return False
    else:
        logged_in_user_id = session['logged_in_user']
        trip = Trip.query.get(trip_id)
        share = Share.query.filter_by(trip_id=trip_id, viewer_id=logged_in_user_id).first()
        if trip.user_id == logged_in_user_id or share:
            return True
        else:
            return False


@app.route('/')
def index():
    """Homepage."""
    if session.get('logged_in_user'):
        user_id = session['logged_in_user']
        user_trips = Trip.query.filter_by(user_id=user_id).all()
        shared_trips = Share.query.filter_by(viewer_id=user_id).all()
    else:
        user_trips = []
        shared_trips= []

    return render_template("homepage.html", trips=user_trips, shared_trips=shared_trips)



@app.route('/create-account', methods=['POST'])
def check_create():
    """ Checks user email is new and processes registration """

    user_email = request.form.get('email')
    user_password = request.form.get('password')
    name = request.form.get('name')

    # Encode password
    hashed_password = bcrypt.hashpw(user_password.encode('utf8'), bcrypt.gensalt(9))

    user = User.query.filter_by(email=user_email).all()

    if user:
        flash("User email already exists")
        return redirect('/login-form')
    else:
        new_user = User(email=user_email, password=hashed_password, name=name)
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
        if bcrypt.checkpw(user_password.encode('utf8'), user.password.encode('utf8')):
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

    if not has_access(trip_id):
        flash("You do not have permission to view this page")
        return redirect('/')
    else:
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

    if not has_access(trip_id):
        flash("You do not have permission to view this page")
        return redirect('/')
    else:    
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


@app.route('/share-trip/<trip_id>', methods=['POST'])
def share_trip(trip_id):
    """make trie viewable by another user"""

    share_email = request.form.get("shareEmail")

    user = User.query.filter_by(email=share_email).one()
    if user:
        user_id = user.user_id
        if Share.query.filter_by(viewer_id=user_id, trip_id=trip_id).one():
            flash("You have already shared with this user")
            return redirect('/trip/%s' % (trip_id))
        else:
            share = Share(viewer_id=user_id, trip_id=trip_id)
            db.session.add(share)
            db.session.commit()
            return redirect('/trip/%s' % (trip_id))

    else:
        flash("No user with that email")
        return redirect('/trip/%s' % (trip_id))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    connect_to_db(app)
    app.run(port=5000, host='0.0.0.0')
