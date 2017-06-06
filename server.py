from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for, jsonify)
from model import User, Trip, Entry, Category, Share, connect_to_db, db, Friend
import os
from werkzeug.utils import secure_filename
import bcrypt
from helper_functions import allowed_file, has_access, send_registration_email, send_notification_email, ALLOWED_EXTENSIONS, send_share_request_email

app = Flask(__name__)

# Required to use Flask sessions
# app.secret_key = os.environ['SECRET_KEY']
app.secret_key = 'abcde'
app.jinja_env.undefined = StrictUndefined
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def index():
    """Homepage."""
    if session.get('logged_in_user'):
        user_id = session['logged_in_user']
        user_trips = Trip.query.filter_by(user_id=user_id).all()
        friends = User.query.get(user_id).all_friends
        friend_ids = [friend.user_id for friend in friends]
        friends_trips = Trip.query.filter(Trip.user_id.in_(friend_ids)).all()
        shared_trips = set([])
        for trip in friends_trips:
            for share in trip.shares:
                if share.viewer_id == user_id:
                    shared_trips.add(trip.trip_id)
    else:
        user_trips = []
        friends_trips = []
        shared_trips = []

    return render_template("homepage.html", trips=user_trips, friends_trips=friends_trips, shared_trips=shared_trips)


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
        return redirect('/')
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

    if not has_access(trip_id, session):
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

    return redirect('/trip/%s' % (trip_id))


@app.route('/entry/<entry_id>')
def view_entry(entry_id):
    """Show entry details"""

    # trip_id = int(trip_id)
    # print trip_id
    entry = Entry.query.get(entry_id)
    trip_id = entry.trip_id
    if not has_access(trip_id, session):
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


@app.route('/share-trip/<trip_id>.json', methods=['POST'])
def share_trip(trip_id):
    """make trie viewable by another user"""

    share_email = request.form.get("email")
    user_id = session['logged_in_user']
    sharer_name = User.query.get(user_id).name
    trip_location = Trip.query.get(trip_id).location
    trip_link = 'http://localhost:5000/trip/' + trip_id

    share_results = {}
    user = User.query.filter_by(email=share_email).all()
    if user:
        user_id = user[0].user_id
        if Share.query.filter_by(viewer_id=user_id, trip_id=trip_id).all():
            share_results['share_status'] = 'already shared'
            return jsonify(share_results)
        else:
            share = Share(viewer_id=user_id, trip_id=trip_id)
            db.session.add(share)
            db.session.commit()
            send_notification_email(share_email, sharer_name, trip_location, trip_link)
            share_results['share_status'] = 'success'
            return jsonify(share_results)

    else:
        share_results['share_status'] = 'no user'
        return jsonify(share_results)


@app.route('/request-friend.json', methods=['POST'])
def request_friend():
    """initiate friend request"""

    friend_email = request.form.get("email")
    user_id = session['logged_in_user']
    user = User.query.get(user_id)

    request_results = {}
    friend = User.query.filter_by(email=friend_email).all()
    if friend:
        if friend[0] in user.all_friends:
            request_results['request_status'] = 'already friends'
            print request_results
            return jsonify(request_results)
        else:
            friend_id = friend[0].user_id
            friend = Friend(requester_id=user_id, accepter_id=friend_id)
            db.session.add(friend)
            db.session.commit()
            request_results['request_status'] = 'success'
            return jsonify(request_results)

    else:
        request_results['request_status'] = 'no user'
        return jsonify(request_results)


@app.route('/invite-user', methods=['POST'])
def invite_user():
    """Invite new user to join with an email"""

    user_email = request.form.get('inviteEmail')
    user_id = session['logged_in_user']
    inviter_name = User.query.get(user_id).name
    send_registration_email(user_email, inviter_name)
    return redirect('/')


@app.route('/friends')
def show_friends():
    """Show friends and friend requests"""

    user_id = session['logged_in_user']
    user = User.query.get(user_id)
    friends = user.all_friends
    friend_requests = user.accepted_friends
    friend_requests = [request for request in friend_requests if request.accepted is None]

    return render_template('friends.html', friends=friends, friend_requests=friend_requests)


@app.route('/accept-friend.json', methods=['POST'])
def accept_friend():
    """Accept users friend request"""

    friend_id = request.form.get("response")
    friend = Friend.query.get(friend_id)
    friend.accepted = True
    db.session.commit()

    response = {'request_id': friend_id}
    return jsonify(response)


@app.route('/deny-friend.json', methods=['POST'])
def deny_friend():
    """Accept users friend request"""

    friend_id = request.form.get("response")
    friend = Friend.query.get(friend_id)
    friend.accepted = False
    db.session.commit()

    response = {'request_id': friend_id}
    return jsonify(response)


@app.route('/share-request.json', methods=['POST'])
def share_request():
    """Send email notifying user of share request"""

    trip_id = request.form.get("trip_id")
    trip = Trip.query.get(trip_id)
    to_email = trip.user.email
    requester = User.query.get(session['logged_in_user']).name
    location = trip.location
    link = 'http://localhost:5000/trip/' + trip_id

    send_share_request_email(to_email, requester, location, link)

    response = {'request_id': trip_id}
    return jsonify(response)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    connect_to_db(app)
    app.run(port=5000, host='0.0.0.0')
