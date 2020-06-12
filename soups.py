import requests
from bs4 import BeautifulSoup

headers = requests.utils.default_headers()

soups = {}  # for storage of soup objects


def get(url):
    '''Returns (with saving) soup objects'''
    if url not in soups:
        page = requests.get(url, headers=headers).text
        soup = BeautifulSoup(page, 'html.parser')
        soups.update({url: soup})
    return soups[url]
