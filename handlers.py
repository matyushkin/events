import re
import datetime
import files

import langs
import urls

current_date = datetime.date.today()

def title(text, name):
    """Обработка заголовков событий"""
    return text


def event_url(url, name):
    url = urls.utm_cleaner(url)
    url = urls.add_home(url, files.pages[name]['start_url'])
    return url


def time(text, name):
    if name == 'Яндекс':
        pattern = re.compile(r'\d{2}:\d{2}')
        time_string = pattern.search(text)
        time_string = time_string.group()
        return time_string


def online_status(text, name):
    if text in ('Online', 'Будет трансляция',
                  'Прямая трансляция', 'Прямой эфир'):
        return 'Online'
    else:
        return 'Offline'


def date(date_string, name):
    if name == 'Яндекс':
        '''Parsing date in format вт, 9 июня'''
        lang = 'rus'
        if 'сегодня' in date_string.lower():
            event_date = current_date
            return event_date.isoformat()
        else:
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


def registration_opened(text, name):
    if name == 'Яндекс':
        if 'открыт' in text:
            return "True"
        else:
            return "False"