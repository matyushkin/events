# compressing and uncompressing soup structures
import os
import pickle
import bz2

# for footers loading and clicking
from selenium import webdriver
os.environ['MOZ_HEADLESS'] = '1'  # Headless Mozilla for Selenium

import requests
from bs4 import BeautifulSoup

import files

headers = requests.utils.default_headers()
path = "files/soups.bz2"


def read_soups():
    with open(path, "rb") as f:
        decompressed = bz2.decompress(f.read())
        return pickle.loads(decompressed)


soups = read_soups()

def write_soups(soups):
    with open(path, "wb") as f:
        pickled = pickle.dumps(soups)
        compressed = bz2.compress(pickled)
        f.write(compressed)


def footer_load(url, num=1, selector="events__more"):
    driver = webdriver.Firefox()
    driver.get(url)
    for i in range(num):
        footer = driver.find_elements_by_class_name(selector)[-1]
        footer.click()
    html_from_page = driver.page_source
    driver.close()
    return html_from_page


def get(url, start_url, force=False):
    '''Returns (with saving) soup objects'''
    if force or url not in soups:
        if url == start_url and files.pages_info[start_url]['load'] == 'with_footer':
            footer_clicks = files.pages_info[start_url]['footer_clicks']
            page = footer_load(url, num=footer_clicks, selector="events__more")
        else:
            page = requests.get(url, headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')
        soups.update({url: soup})
    else:
        soup = soups[url]
    # remove all javascript and stylesheet code
    for script in soup(["script", "style", "iframe"]):
        script.extract()
    return soup
