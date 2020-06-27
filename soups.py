# compressing and uncompressing soup structures
import pickle
import bz2

import requests
from bs4 import BeautifulSoup

headers = requests.utils.default_headers()
path = "files/soups.bz2"


with open(path, "rb") as f:
    decompressed = bz2.decompress(f.read())
    soups = pickle.loads(decompressed)


def get(url, force):
    '''Returns (with saving) soup objects'''
    if force or url not in soups:
        page = requests.get(url, headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')
        soups.update({url: soup})
        with open(path, "wb") as f:
            pickled = pickle.dumps(soups)
            compressed = bz2.compress(pickled)
            f.write(compressed)

    else:
        soup = soups[url]
    # remove all javascript and stylesheet code
    for script in soup(["script", "style", "iframe"]):
        script.extract()
    return soup
