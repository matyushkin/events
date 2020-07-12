import math
import sys
import os
import copy
import re
import importlib
import itertools
import json

import pandas as pd
from bs4 import BeautifulSoup

# custom packages
import files
import soups
import urls
import langs
import handlers


class StartPage:
    """Парсинг начальных страниц, описанных в pages.json"""
    def __init__(self, start_url):
        self.data, self.event_lists, self.events = {}, {}, {}
        self.data['start_url'] = start_url
        self.data['soup'] = soups.get_soup(start_url, start_url)
        self.fields = files.fields_order(start_url)
        for field in self.fields['start']:
            self.event_lists[field] = files.get_content(self.data, field)
        event_urls = self.event_lists.pop('event_url')
        self.fields['start'].remove('event_url')
        for i, event_url in enumerate(event_urls):
            self.events[event_url] = {}
            for field in self.fields['start']:
                self.events[event_url][field] = self.event_lists[field][i]
    
    def __repr__(self):
        return self.actual_events
                     
    @property
    def actual_events(self):
        """События, актуальные на текущий день"""
        events = self.events.copy()
        for event_url in self.events:
            if events[event_url]['date'] < handlers.current_date.isoformat():
                events.pop(event_url)
        return events


class EventPage:
    """Парсинг страниц событий"""
    def __init__(self, event_url, start_page):
        self.data = start_page.events[event_url]
        self.data['start_url'] = start_page.data['start_url']
        self.data['event_url'] = event_url
        self.data['soup'] = soups.get_soup(self.data['start_url'], event_url)
        for field in start_page.fields['event']:
            self.data[field] = files.get_content(self.data, field)
        for field in self.data:
            # удаление дупликатов в списках с сохранением порядка
            if type(self.data[field]) == list:
                self.data[field] = list(dict.fromkeys(self.data[field]))