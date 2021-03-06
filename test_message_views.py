"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser", email="test@test.com", password="testuser", image_url=None)
        self.testuser_id = 531
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_unauthorized_new_message_access(self):
        """Test that if no user is added to the session that there is no authorization to add a message."""
        with self.client as c:
            res = c.post("/messages/new", data={"text": "Testing Unauthorization"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))

    def test_add_invalid_user(self):
        """Test to detect that 'access unauthorized' will kick in when the user_id does not exist."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9999999

            res = c.post("/messages/new", data={"text": "Invalid User Id"}, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))

    def test_message_show(self):
        """Test to detect that when an authorized user posts a valid message, the message shows."""
        m = Message(id=123456, text="Yes this message should show!", user_id=self.testuser.id)

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message.query.get(123456)

            res = c.get(f"/messages/{m.id}")

            self.assertEqual(res.status_code, 200)
            self.assertIn(m.text, str(res.data))

    def test_invalid_message_show(self):
        """Test that 404 page/message will kick in for an invalid message id"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get("/messages/9ujh8y689")

            self.assertEqual(res.status_code, 404)

    def test_message_delete(self):
        """Test that message will successfully delete"""
        m = Message(id=98765, text="Message Delete Test", user_id=self.testuser.id)

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post("/messages/98765/delete", follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            m = Message.query.get(98765)
            self.assertIsNone(m)

    def test_message_delete(self):
        """Test to make sure that someone that doesn't own the message cannot delete it."""
        m = Message(id=9911, text="Not allowed to delete me", user_id=self.testuser.id)

        db.session.add(m)
        db.session.commit()

        u = User.signup(username="tryToDeleteMsg", email="cannotdeleteothersmessages@gmail.com", password="password", image_url=None)
        u.id = 121212

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = u.id

            res = c.post("/messages/9911/delete", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Unauthorized", str(res.data))

            m = Message.query.get(9911)
            self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):
        """Test that message will not delete when no user is logged in."""
        m = Message(id=2012, text="This message will not delete either!!!", user_id=self.testuser.id)

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            res = c.post("/messages/2012/delete", follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))

            m = Message.query.get(2012)
            self.assertIsNotNone(m)