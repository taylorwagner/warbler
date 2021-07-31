"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test model for user."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        SantanaRP = User.signup("SanRushTest", "srptest@email.com", "password", None)
        SantanaRPid = 1111
        SantanaRP.id = SantanaRPid

        ExodusAP2 = User.signup("ExAeroTest", "eaptest@email.com", "password", None)
        ExodusAP2id = 2222
        ExodusAP2.id = ExodusAP2id

        db.session.commit()

        SantanaRP = User.query.get(SantanaRPid)
        ExodusAP2 = User.query.get(ExodusAP2id)

        self.SantanaRP = SantanaRP
        self.SantanaRPid = SantanaRPid

        self.ExodusAP2 = ExodusAP2
        self.ExodusAP2id = ExodusAP2id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does repr method work for user model?"""
        self.assertEqual(self.SantanaRP.__repr__, "<User #1111: SanRushTest, srptest@email.com>")

    ## FOLLOW TESTS:

    def test_is_following(self):
        """Does is_following successfully detect when one user is following another user?"""
        self.SantanaRP.following.append(self.ExodusAP2)
        db.session.commit()

        self.assertEqual(len(self.ExodusAP2.following), 0)
        self.assertEqual(len(self.SantanaRP.following), 1)

        self.assertEqual(self.SantanaRP.following[0].id, self.ExodusAP2.id)

        self.assertTrue(self.SantanaRP.is_following(self.ExodusAP2))
        self.assertFalse(self.ExodusAP2.is_following(self.SantanaRP))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when one user is being followed by another user?"""
        self.SantanaRP.following.append(self.ExodusAP2)
        db.session.commit()

        self.assertEqual(len(self.ExodusAP2.followers), 1)
        self.assertEqual(len(self.SantanaRP.followers), 0)

        self.assertEqual(self.ExodusAP2.followers[0].id, self.SantanaRP.id)

        self.assertTrue(self.ExodusAP2.is_followed_by(self.SantanaRP))
        self.assertFalse(self.SantanaRP.is_followed_by(self.ExodusAP2))

    ## AUTHENTICATION TESTS:

    def test_valid_authentication(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        u = User.authenticate(self.SantanaRP.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.SantanaRPid)

    def test_invalid_username(self):
        """Does User.authenticate fail to return a user when username is invalid?"""
        self.assertFalse(User.authenticate("aljgs;lkj", "password"))

    def test_wrong_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        self.assertFalse(User.authenticate(self.SantanaRP.username, "lakjgs;as"))