#!/usr/bin/env python3

'''
Processing and compressing of BeautifulSoup structures
'''

from selenium import webdriver
import files
from bs4 import BeautifulSoup
import requests

import os
import time

import sqlite3
from sqlite3 import Error
path = "files/HTML.sqlite"

headers = requests.utils.default_headers()


os.environ['MOZ_HEADLESS'] = '1'  # Headless Mozilla for Selenium


# if time.time() - os.path.getmtime(path) >= 4*3060:
#     # Если прошло не менее 4 часов с обновления базы данных
#     print('Обновляем базу данных...')
#     FORCE = True
# else:
#     FORCE = False

FORCE = True


def execute_read_query(query):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def write_HTML(url: str, html: str):
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        create_html_table = """
        CREATE TABLE IF NOT EXISTS html (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          url_str TEXT NOT NULL,
          html_str TEXT NOT NULL
        );
        """

        insert_html = f"""
        INSERT OR REPLACE INTO
            html (id, url_str, html_str)
        VALUES ((SELECT id FROM html WHERE url_str = ?), ?, ?)"""

        cursor.execute(create_html_table)
        cursor.execute(insert_html, (url, url, html))
        connection.commit()
    except Error as e:
        print('Не удалось обработать {url}')



def read_HTML(url: str):
    select_HTML = f"""
    SELECT html_str
    FROM html
    WHERE url_str = '{url}'
    """
    html = execute_read_query(select_HTML)
    if html:
        return html[0][0]
    else:
        return ''


def simple_load(url):
    print(f'Загружаем данные со страницы {url}')
    page = requests.get(url, headers=headers).text
    return page


def multiple_load(url, root, start, stop_selector):
    first_page = simple_load(url)
    total_soup = BeautifulSoup(first_page, 'html.parser')
    num = start
    while True:
        url = f'{root}{num}'
        page = simple_load(url)
        if stop_selector not in page:
            break
        else:
            soup = BeautifulSoup(page, 'html.parser')
            for child in soup.body.findChildren(recursive=False):
                total_soup.body.append(child)
            num += 1
    return str(total_soup)


def footer_load(url, num, selector):
    driver = webdriver.Firefox()
    driver.get(url)
    for i in range(num):
        footer = driver.find_elements_by_class_name(selector)[-1]
        footer.click()
    html_from_page = driver.page_source
    driver.close()
    return html_from_page


def get_page(url, start_url, force):
    '''Returns (with saving) s objects'''
    if force and (url == start_url):
        info = files.pages_info[start_url]
        if files.pages_info[start_url]['load'] == 'with_footer':
            footer_clicks = info.get('footer_clicks', 1)
            selector = info.get('footer_selector')
            page = footer_load(url, footer_clicks, selector)
        elif files.pages_info[start_url]['load'] == 'multiple':
            root = info.get("multiple_root")
            start = info.get("multiple_start", 2)
            stop_selector = info.get("multiple_stop_selector")
            page = multiple_load(start_url, root, start, stop_selector)
        else:
            page = simple_load(url)
    elif force and (url != start_url):
        page = simple_load(url)
    else:
        page = read_HTML(url)
        if not page:
            page = simple_load(url)
            soup = BeautifulSoup(page, 'html.parser')
            for script in soup(["script", "style", "iframe"]):
                script.extract()
            page = str(soup)
            write_HTML(url, page)
    return page


def get(url, start_url, force=FORCE):
    page = get_page(url, start_url, force)
    soup = BeautifulSoup(page, 'html.parser')
    return soup


def force_update_soups():
    urls = [s[0]for s in execute_read_query("SELECT url_str FROM html")]
    for url in urls:
        event_url_data = files.events.get(url)
        if event_url_data:
            start_url = event_url_data.get('start_url')
        else:
            start_url = url
        get(url, start_url, force=True)