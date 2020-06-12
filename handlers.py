import re
import datetime
import files

import langs
import urls

current_date = datetime.date.today()


def event_url(event_url, name):
    start_url = files.pages[name]['start_url']
    event_url = urls.utm_cleaner(event_url)
    event_url = urls.add_home(event_url, start_url)
    return event_url


def time(time, name):
    if name == 'Яндекс':
        pattern = re.compile(r'\d{2}:\d{2}')
        time = pattern.search(time)
        time = time.group()
        return time


def online_status(online_status, name):
    if status in ('Online', 'Будет трансляция',
                  'Прямая трансляция', 'Прямой эфир'):
        return 'Online'
    else:
        return 'Offline'


def date(date_string, name):
    if name == 'Яндекс':
        '''Parsing date in format вт, 9 июня'''
        lang = 'rus'
        weekdays = langs.date_alias[lang]['weekdays']['short']
        months = langs.date_alias[lang]['months']['gentive']

        weekday, event_day, month = date_string.split()
        event_day = int(event_day)
        event_month = months.index(month) + 1
        event_weekday = weekdays.index(weekday[:-1])
        event_year = current_date.year

        # Case for the end of year: too old events are not in list
        # but there can be next year events pages in the last half of current year
        if (event_month-current_date.month) < -3:
            event_year += 1

        event_date = datetime.date(event_year, event_month, event_day)
        if event_date.weekday() == event_weekday:
            return event_date.isoformat()
