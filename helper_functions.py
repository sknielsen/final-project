from model import User, Trip, Share
import sendgrid
import os
from sendgrid.helpers.mail import *


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


def send_registration_email(to_email, inviter):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("trips@sojournal.com")
    to_email = Email(to_email)
    subject = "Your friend has invited you to join SOJOURNAL!"
    content = Content("text/html", "<p>" + inviter + " has invited you to join SOJOURNAL, an online travel journal to keep track of all your adventures and share them with friends!<br><br>Click <a href=\"http://localhost:5000\">here</a> to register.</p>")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


def send_notification_email(to_email, sharer, location, link):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("trips@sojournal.com")
    to_email = Email(to_email)
    subject = "Your friend has shared their trip with you!"
    content = Content("text/html", "<p>" + sharer + " has shared their trip to " + location + " with you!</p><br><br>Click <a href=\"" + link + "\">here</a> to see the trip.</p>")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
