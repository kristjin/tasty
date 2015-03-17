__author__ = 'kristjin@github'

import os
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tasty.config.TestingConfig"

import unittest
import json
from urlparse import urlparse

from tasty import app
from tasty import models
from tasty.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the posts API """






    def testCreateIngredient(self):
        """ Test Creating Ingredient """

        response = self.client.post("/api/flavor?name=macadamia nuts",
                                    headers=[("Accept", "application/json")],
                                    )

        # Verify request to endpoint was successful using 201 created
        self.assertEqual(response.status_code, 201)
        # Verify that the response is JSON type
        self.assertEqual(response.mimetype, "application/json")
        # Verify the endpoint is setting the correct Location header
        # This should be the link to the new post
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/flavor/id/1")
        # Decode the response with json.loads
        data = json.loads(response.data)
        # Validate the response
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "macadamia nuts")
        # Query DB to validate status
        data = session.query(models.Flavor).all()
        print data
        # Verify only one item in DB
        self.assertEqual(len(data), 1)
        # Isolate the one item in the list
        data = data[0]
        print data
        # Validate the content of the item retrieved from the DB
        self.assertEqual(data.id, 1)
        self.assertEqual(data.name, "macadamia nuts")


    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()