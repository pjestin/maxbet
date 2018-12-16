import unittest
from core.common import download
import os
from datetime import datetime


TEST_FILE_PATH = 'core/test/common/test_file.html'
TEST_URL = 'https://www.google.ie/'


class DownloadTest(unittest.TestCase):

    @classmethod
    def clean(cls):
        if os.path.isfile(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)

    def setUp(self):
        self.clean()

    def tearDown(self):
        self.clean()

    def test_download_data(self):
        self.assertFalse(os.path.isfile(TEST_FILE_PATH))
        download.download_data(TEST_URL, TEST_FILE_PATH)
        self.assertTrue(os.path.isfile(TEST_FILE_PATH))
        file_time = datetime.fromtimestamp(os.path.getmtime(TEST_FILE_PATH))
        download.download_data(TEST_URL, TEST_FILE_PATH)
        new_file_time = datetime.fromtimestamp(os.path.getmtime(TEST_FILE_PATH))
        self.assertEqual(file_time, new_file_time)
