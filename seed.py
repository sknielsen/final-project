from model import Category
from model import connect_to_db, db
from server import app


def load_categories():
    """Load categories from category.txt into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate categories
    Category.query.delete()

    # Read file and insert data
    for row in open("categories.txt"):
        row = row.rstrip()
        name = row

        category = Category(name=name)

        # We need to add to the session or it won't ever be stored
        db.session.add(category)

    # Once we're done, we should commit our work
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_categories()
