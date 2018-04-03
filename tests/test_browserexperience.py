from flask_testing import LiveServerTestCase
from iiifcollectionbrowse import app
import os
from selenium import webdriver
import unittest
import urllib

class TestBase(LiveServerTestCase):
    def create_app(self):
        app.config.update(LIVESERVER_PORT=8943)
        return app

    def setUp(self):
        os.environ["IIIFCOLLBROWSE_DEFAUL_COLL"] = "https://iiif-collection.lib.uchicago.edu//top.json"
        self.driver = webdriver.Firefox()
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()

    def test_server_is_up_and_running(self):
        response = urllib.request.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

if __name__ == "__main__":
    unittest.main()