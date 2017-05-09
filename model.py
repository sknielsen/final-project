from flask_sqlalchemy import SQLAlchemy

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
    note = db.Column(db.String(255), nullable=True)
    photo_location = db.Column(db.String(255),  nullable=False)
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

##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///travels'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."