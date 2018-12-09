#! /usr/bin/env python3
# coding: utf-8

import os
import datetime
import urllib.request


MAX_FILE_AGE_MINUTES = 60


def download_data(url, file_path):
    download = False
    if not os.path.isfile(file_path):
        download = True
    else:
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        file_age = datetime.datetime.today() - file_time
        print('File age: {}'.format(file_age))
        if file_age >= datetime.timedelta(minutes=MAX_FILE_AGE_MINUTES):
            download = True
    if download:
        print('Downloading data file from URL {}'.format(url))
        urllib.request.urlretrieve(url, file_path)
