#! /usr/bin/env python3
# coding: utf-8

import os
import datetime
import urllib.request
from urllib.error import URLError
import logging


MAX_FILE_AGE_MINUTES = 1


def download_data(url, file_path):
    download = False
    if not os.path.isfile(file_path):
        download = True
    else:
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        file_age = datetime.datetime.today() - file_time
        logging.info('File age: {}'.format(file_age))
        if file_age >= datetime.timedelta(minutes=MAX_FILE_AGE_MINUTES):
            download = True
    if download:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        logging.info('Downloading data file from URL {}'.format(url))
        urllib.request.urlretrieve(url, file_path)


def get_page(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        return urllib.request.urlopen(req).read()
    except URLError as e:
        logging.error('Error while trying to get page {}: {}'.format(url, e))
    except:
        logging.error('Error while trying to get page {}'.format(url))
    return None
