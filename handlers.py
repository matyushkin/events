import re
import datetime
import files

import langs
import urls

current_date = datetime.date.today()
tomorrow = current_date + datetime.timedelta(days=1)

def title(text, page_data):
    """Обработка заголовков событий"""
    return text


def event_url(url, page_data):
    url = urls.utm_cleaner(url)
    url = urls.add_home(url, page_data['start_url'])
    return url


def reg_url(url, page_data):
    url = urls.utm_cleaner(url)
    if url[0] == '#':
        url = page_data['event_url'] + url
    return url


def time(text, page_data):
    if page_data['start_url'] == 'https://events.yandex.ru/':
        pattern = re.compile(r'\d{2}:\d{2}')
        time_string = pattern.search(text)
        time_string = time_string.group()
        return time_string


def online_status(text, page_data):
    if text in ('Online', 'Будет трансляция',
                  'Прямая трансляция', 'Прямой эфир'):
        return 'Online'
    else:
        return 'Offline'


def date(date_string, page_data):
    if 'сегодня' in date_string.lower():
        return current_date.isoformat()
    elif 'завтра' in date_string.lower():
        return tomorrow.isoformat()

    if page_data['start_url'] == 'https://events.yandex.ru/':
        '''Parsing date in format вт, 9 июня and 22 июля'''
        lang = 'rus'
        months = langs.date_alias[lang]['months']['gentive']

        event_year = current_date.year

        month_flags = [date_string.find(month) for month in months]
        month_ind = month_flags.index(max(month_flags))
        event_month = month_ind + 1
        
        # Day is pre
        m = date_string.split().index(months[month_ind])
        event_day = int(date_string.split()[m-1])

        # Case for the end of year: too old events are not in list
        # but there can be next year events pages in the last half of current year
        if (event_month-current_date.month) < -3:
            event_year += 1

        event_date = datetime.date(event_year, event_month, event_day)
        return event_date.isoformat()


def registration_opened(text, page_data):
    if page_data['start_url'] == 'https://events.yandex.ru/':
        if 'открыт' in text:
            return "True"
        else:
            return "False"


def organizers(list_of_organizers, page_data):
    return list_of_organizers


def location(location_string, page_data):
    if location_string.lower() in ["онлайн", "online"]:
        location_string = "Online"
    return location_string


def description(list_of_descriptions, page_data):
    return  list_of_descriptions


def themes(theme, page_data):
    bad_themes = ['Регистрация',
                  'Приветствие модератора',
                  'Начало регистрации',
                  'Общение',
                  'Заказываем пиццу и ставим оценки мероприятию']
    if theme in bad_themes:
        theme = ''
    return theme


def speakers(speaker, page_data):
    return speaker


def speakers_companies(speaker_company, page_data):
    return speaker_company


def price(price_string, page_data):
    return price_string


