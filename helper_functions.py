from model import User, Trip, Share

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def has_access(trip_id, session):
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