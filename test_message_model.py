"""Message model tests."""
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 1017
        u = User.signup("test1", "email1@email.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(text="testmessage", user_id=self.uid)

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "testmessage")

    def test_message_likes(self):
        """Test to verify that likes are being detected on messages."""
        m1 = Message(text="ilovetesting", user_id=self.uid)

        m2 = Message(text="learning a lot in warbler", user_id=self.uid)

        u = User.signup("testusersignup", "testingtesting@test.com", "password", None)
        uid = 121
        u.id = uid
        db.session.add_all([m1, m2, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        # self.assertEqual(len(1), 1)
        self.assertEqual(l[0].message_id, m1.id)