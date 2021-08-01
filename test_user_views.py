"""User view tests."""

import os
from unittest import TestCase
from models import db, connect_db, Message, User, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="sanrushpor1", email="srptest@gmail.com", password="testsantana", image_url=None)
        self.testuser_id = 917
        self.testuser.id = self.testuser_id

        self.user1 = User.signup("ExPorter", "fakeemail@aol.com", "password", None)
        self.user1_id = 1216
        self.user1.id = self.user1_id
        self.user2 = User.signup("LeoPeezy3", "lenopatport2@gmail.com", "password", None)
        self.user2_id = 710
        self.user2.id = self.user2_id
        self.user3 = User.signup("MegLP6", "bakingitup@fake.com", "password", None)
        self.user4 = User.signup("PaulieFBaby7", "isnotreal@email.com", "password", None)

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_users_index(self):
        """Test feature that list_users"""
        with self.client as c:
            res = c.get('/users')

            self.assertIn("@sanrushpor1", str(res.data))
            self.assertIn("@ExPorter", str(res.data))
            self.assertIn("@LeoPeezy3", str(res.data))
            self.assertIn("@MegLP6", str(res.data))
            self.assertIn("@PaulieFBaby7", str(res.data))

    def test_users_search(self):
        """Test feature on list_users that allows users to be searched for with q param"""
        with self.client as c:
            res = c.get('/users?q=san')

            self.assertIn("@sanrushpor1", str(res.data))

            self.assertNotIn("@ExPorter", str(res.data))
            self.assertNotIn("@LeoPeezy3", str(res.data))
            self.assertNotIn("@MegLP6", str(res.data))
            self.assertNotIn("@PaulieFBaby7", str(res.data))

    def test_user_show(self):
        """Test user profile page"""
        with self.client as c:
            res = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(res.status_code, 200)

            self.assertIn("@sanrushpor1", str(res.data))

    def setup_followers(self):
        """Create test client, add sample data for followers"""
        f1 = Follows(user_being_followed_id=self.user1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.user2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.user1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_user_show_with_followers(self):
        """Test user_show to see if followers are being detected"""
        self.setup_followers()
        with self.client as c:
            res = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(res.status_code, 200)

            self.assertIn("@sanrushpor1", str(res.data))
            soup = BeautifulSoup(str(res.data), "html.parser")
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 0 messages
            self.assertIn("0", found[0].text)

            # Test for a count of 2 following
            self.assertIn("2", found[1].text)

            # Test for a count of 1 follower
            self.assertIn("1", found[2].text)

    def test_show_following(self):
        """Test show_following to see if followed users are detected"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f"/users/{self.testuser_id}/following")

            self.assertEqual(res.status_code, 200)

            self.assertIn("@ExPorter", str(res.data))
            self.assertIn("@LeoPeezy3", str(res.data))
            self.assertNotIn("@MegLP6", str(res.data))
            self.assertNotIn("@PaulieFBaby7", str(res.data))

    def test_show_followers(self):
        """Test users_followers to see if users that are following are detected"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f"/users/{self.testuser_id}/followers")

            self.assertEqual(res.status_code, 200)

            self.assertIn("@ExPorter", str(res.data))
            self.assertNotIn("@LeoPeezy3", str(res.data))
            self.assertNotIn("@MegLP6", str(res.data))
            self.assertNotIn("@PaulieFBaby7", str(res.data))

    def test_unauthorized_following_page_access(self):
        """"""
        self.setup_followers()