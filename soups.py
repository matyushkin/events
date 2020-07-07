# compressing and uncompressing s structures
from bs4 import BeautifulSoup
import requests
import files
import os
import pickle
import bz2

# for footers loading and clicking
from selenium import webdriver
os.environ['MOZ_HEADLESS'] = '1'  # Headless Mozilla for Selenium


headers = requests.utils.default_headers()

def read_ss():
    try:
        with open("files/soups.bz2", "rb") as f:
            decompressed = bz2.decompress(f.read())
            return pickle.loads(decompressed)
    except EOFError:
        print('Warning: ss bz2 file is empty')
        return {}


def write_ss(ss):
    with open("files/soups.bz2", "wb") as f:
        pickled = pickle.dumps(ss)
        f.write(bz2.compress(pickled))


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
    '''Returns (with saving) s objects'''
    if force or (url not in ss):
        print(f'Загружаем страницу {url}')
        if url == start_url and files.pages_info[start_url]['load'] == 'with_footer':
            footer_clicks = files.pages_info[start_url]['footer_clicks']
            page = footer_load(url, num=footer_clicks, selector="events__more")
        else:
            page = requests.get(url, headers=headers).text
        s = BeautifulSoup(page, 'html.parser')
        for script in s(["script", "style", "iframe"]):
            script.extract()
        ss.update({url: s})
        write_ss(ss)
    else:
        s = ss[url]
    return s


def force_update_ss():
    for url in files.ss.ss.keys():
        event_url_data = files.events.get(url)
        if event_url_data:
            start_url = event_url_data.get('start_url')
        else:
            start_url = url
        get(url, start_url, force=True)

ss = read_ss()