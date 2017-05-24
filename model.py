from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

##############################################################################
# Model definitions


class User(db.Model):
    """User of travel journal website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User name=%s email=%s>" % (self.name, self.email)


class Trip(db.Model):
    """Trip in travel journal website."""

    __tablename__ = "trips"

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    location = db.Column(db.String(64), nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("trips",
                                              order_by=trip_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Trip location=%s>" % (self.location)


class Entry(db.Model):
    """Entries in trip in travel journal website."""

    __tablename__ = "entries"

    entry_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))
    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64), nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    photo_location = db.Column(db.String(255),  nullable=True)
    type_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'))

    # Define relationship to trip
    trip = db.relationship("Trip",
                            backref=db.backref("entries",
                                               order_by=entry_id))

    # Define relationship to category
    category = db.relationship("Category",
                            backref=db.backref("entries",
                                               order_by=entry_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Entry location=%s>" % (self.name)


class Category(db.Model):
    """Categories for entry in travel journal website."""

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Category name=%s>" % (self.name)


class Share(db.Model):
    """Shows who can view what trip"""

    __tablename__ = "shares"

    share_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    viewer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.trip_id'))

    # Define relationship to trip
    trip = db.relationship("Trip",
                            backref=db.backref("shares",
                                               order_by=share_id))

    # Define relationship to user
    user = db.relationship("User",
                            backref=db.backref("shares",
                                               order_by=share_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Trip=%s shared with user=%s>" % (self.trip.name, self.user.name)


class Friend(db.Model):
    """Create relationship between two users"""

    __tablename__ = "friends"

    friend_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    accepter_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    accepted = db.Column(db.Boolean, nullable=True)

    # Define relationship to user
    requester = db.relationship("User", foreign_keys="Friend.requester_id",
                                        backref=db.backref("requested_friends",
                                        order_by=friend_id))

    # Define relationship to user
    accepter = db.relationship("User", foreign_keys="Friend.accepter_id",
                                       backref=db.backref("accepted_friends",
                                       order_by=friend_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<%s requested to be friends with %s and the status is %s>" % (self.requester.name, self.accepter.name, self.accepted)


# this relationship is viewonly and selects across the union of all friends
friendship_union = db.select([
                    Friend.requester_id,
                    Friend.accepter_id
                    ]).where(Friend.accepted==True).union(
                        db.select([
                            Friend.accepter_id,
                            Friend.requester_id]
                        ).where(Friend.accepted==True)
                    ).alias()


User.all_friends = db.relationship('User',
                       secondary=friendship_union,
                       primaryjoin=User.user_id==friendship_union.c.requester_id,
                       secondaryjoin=User.user_id==friendship_union.c.accepter_id,
                       viewonly=True)



##############################################################################
# Helper functions


def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    User.query.delete()
    Trip.query.delete()
    Entry.query.delete()
    Category.query.delete()
    Share.query.delete()

    # Add sample data
    user1 = User(email='user1@gmail.com', password=bcrypt.hashpw('user1'.encode('utf8'), bcrypt.gensalt(9)), name='One')
    user2 = User(email='user2@gmail.com', password=bcrypt.hashpw('user2'.encode('utf8'), bcrypt.gensalt(9)), name='Two')
    trip1 = Trip(location='Spain', date='08/09/2017', name='Abroad Trip', user_id=1)
    entry1 = Entry(trip_id=1, name='Tibidabo', address='08035 Barcelona, Spain', notes='Fun day trip!',
                   type_id=1)
    category1 = Category(name='Attraction')
    share1 = Share(viewer_id=2, trip_id=1)

    db.session.add_all([user1, user2, trip1, entry1, category1, share1])
    db.session.commit()


def connect_to_db(app, db_uri='postgresql:///travels'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."