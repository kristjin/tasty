__author__ = 'kristjin@github'

import os
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tasty.config.TestingConfig"

import unittest
import json
from urlparse import urlparse
from werkzeug.security import generate_password_hash

from tasty import app
from tasty.models import Flavor, User
from tasty.database import Base, engine, session


class TestViews(unittest.TestCase):
    """ Tests for Tasty! views integration """

    def test

    def testAddFlavor(self):
        """ Test Adding a Flavor """
        # Login
        self.simulate_login()
        # Get response as a result of posting new flavor
        response = self.client.post("/flavor/add", data={
            "flavor": "macadamia nuts"
        })

        self.assertEqual(response.status_code, 302)  # FOUND (as 303 SEE OTHER)
        self.assertEqual(urlparse(response.location).path, "/flavor/1")

        # Verify action completed in DB
        flavors = session.query(Flavor).all()
        self.assertEqual(len(flavors), 1)

        flavor = flavors[0]
        self.assertEqual(flavor.name, "macadamia nuts")
        self.assertEqual(flavor.creator, self.user)


    def simulate_login(self):
        with self.client.session_transaction() as http_session:
            http_session["user_id"] = str(self.user.id)
            http_session["_fresh"] = True


    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User()
        self.user.name = "Alice"
        self.user.email = "alice@example.com"
        self.user.password=generate_password_hash("test")

        session.add(self.user)
        session.commit()

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()