# compressing and uncompressing soup structures
import pickle
import bz2

import requests
from bs4 import BeautifulSoup

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


def get(url, force=False):
    '''Returns (with saving) soup objects'''
    if force or url not in soups:
        page = requests.get(url, headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')
        soups.update({url: soup})
    else:
        soup = soups[url]
    # remove all javascript and stylesheet code
    for script in soup(["script", "style", "iframe"]):
        script.extract()
    return soup
