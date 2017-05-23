import unittest
from model import connect_to_db, db, example_data
from server import app
from flask import session
from helper_functions import allowed_file, has_access, send_registration_email, send_notification_email, ALLOWED_EXTENSIONS


class FlaskTestsBasic(unittest.TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn("SOJOURNAL", result.data)


class TestHelper(unittest.TestCase):

    def test_allowed_file_true(self):
        self.assertTrue(allowed_file('file.jpg'))

    def test_allowed_file_false(self):
        self.assertFalse(allowed_file('file'))

    def test_has_access_false(self):
        self.assertFalse(has_access(1, {}))


class FlaskTestsLoggedOut(unittest.TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_homepage(self):
        """Test that user can't see trips when logged out."""

        result = self.client.get("/", follow_redirects=True)
        self.assertNotIn("Your Trips", result.data)
        self.assertIn("Login", result.data)

    def test_trip_page(self):
        """Test that user can't see trips when logged out."""

        result = self.client.get("/trip/1", follow_redirects=True)
        self.assertNotIn("Add new Entry", result.data)
        self.assertIn("Login", result.data)

    def test_entry_page(self):
        """Test that user can't see trips when logged out."""

        result = self.client.get("/trip/1/1", follow_redirects=True)
        self.assertNotIn("Back to trip", result.data)
        self.assertIn("Login", result.data)


class FlaskTestsLogInLogOut(unittest.TestCase):
    """Test log in and log out."""

    def setUp(self):
        """Before every test"""

        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_logout(self):
        """Test logout route."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['logged_in_user'] = '1'

            result = self.client.get('/logout', follow_redirects=True)

            self.assertNotIn('logged_in_user', session)
            self.assertIn('logged out', result.data)


class FlaskTestsDatabaseNoSession(unittest.TestCase):
    """Flask tests that use the database and no session."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_login_correct(self):
        """Test log in form."""

        with self.client as c:
            result = c.post('/check-login',
                            data={'email': 'user1@gmail.com', 'password': 'user1'},
                            follow_redirects=True
                            )
            self.assertEqual(session['logged_in_user'], 1)
            self.assertIn("Hello, ", result.data)

    def test_login_password(self):
        """Test log in form."""

        with self.client as c:
            result = c.post('/check-login',
                            data={'email': 'user1@gmail.com', 'password': 'user2'},
                            follow_redirects=True
                            )
            self.assertIn("Wrong password!", result.data)

    def test_login_email(self):
        """Test log in form."""

        with self.client as c:
            result = c.post('/check-login',
                            data={'email': 'user3@gmail.com', 'password': 'user1'},
                            follow_redirects=True
                            )
            self.assertIn("No user with that email", result.data)


    def test_create_account_existing(self):
        """Test create account form."""

        with self.client as c:
            result = c.post('/create-account',
                            data={'email': 'user1@gmail.com', 'password': 'user1', 'name': 'One'},
                            follow_redirects=True
                            )
            self.assertIn("User email already exists", result.data)

    def test_create_account_nonexisting(self):
        """Test create account form."""

        with self.client as c:
            result = c.post('/create-account',
                            data={'email': 'user3@gmail.com', 'password': 'user3', 'name': 'Three'},
                            follow_redirects=True
                            )
            self.assertIn("Welcome, Three", result.data)
            self.assertEqual(session['logged_in_user'], 3)


class FlaskTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['SECRET_KEY'] = 'key'
        app.config['TESTING'] = True

        with self.client as c:
            with c.session_transaction() as sess:
                sess['logged_in_user'] = 1

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_homepage_logged_in(self):
        """Test departments page."""

        result = self.client.get("/", follow_redirects=True)
        self.assertNotIn(">Login>/a>", result.data)
        self.assertIn("Your Trips", result.data)

    # def test_departments_details(self):
    #     """Test departments page."""

    #     result = self.client.get("/department/fin")
    #     self.assertIn("Phone: 555-1000", result.data)


if __name__ == "__main__":

    unittest.main()