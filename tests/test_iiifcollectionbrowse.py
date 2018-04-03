import os
import unittest
from unittest.mock import patch
from iiifcollectionbrowse import app
from selenium import webdriver

class Tests(unittest.TestCase):
    @patch.dict(os.environ, {'IIIFCOLLBROWSE_DEFAULT_COLL': 'https://iiif-collection.lib.uchicago.edu/top.json'})
    def setUp(self):
        # Perform any setup that should occur
        # before every test
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        print(app)
        self.app = app.test_client()

    def tearDown(self):
        # Perform any tear down that should
        # occur after every test
        pass

    def testGetDefaultCollection(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testOpeningHomePage(self):
        driver = webdriver.Firefox()
        driver.implicitly_wait(6)
        driver.get("http://localhost:8000/")
        driver.find_element_by_id("content")
        print(driver)
        self.assertEqual(True, False)

if __name__ == "__main__":
    unittest.main()
