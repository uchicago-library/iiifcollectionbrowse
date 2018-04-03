import os
from test.support import EnvironmentVarGuard
import unittest
from unittest.mock import patch
from iiifcollectionbrowse import app
from selenium import webdriver

class Tests(unittest.TestCase):
    def setUp(self):
        # Perform any setup that should occur
        # before every test
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        self.app = app.test_client()

    def tearDown(self):
        # Perform any tear down that should
        # occur after every test
        pass

    def testGetDefaultCollection(self):
        response = self.app.get("/", follow_redirects=True)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def testGetSpecificCollection(self):
        response = self.app.get("/?record=https://iiif-collection.lib.uchicago.edu/rac/rac.json", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
