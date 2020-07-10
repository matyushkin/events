import re
import datetime

import pandas as pd

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
    pattern = re.compile(r'\d{2}:\d{2}')
    time_string = pattern.search(text)
    time_string = time_string.group()
    return time_string


def online_status(text, page_data):
    if text.lower().strip() in ('online', 'будет трансляция',
                  'прямая трансляция', 'прямой эфир',
                  'онлайн-трансляция'):
        return 'Online'
    else:
        return 'Offline'


def date(date_string, page_data):
    '''Parsing date in format вт, 9 июня and 22 июля'''
    # print(date_string)
    if 'сегодня' in date_string.lower():
        return current_date.isoformat()
    elif 'завтра' in date_string.lower():
        return tomorrow.isoformat()

    try:
        lang = 'rus'
        month_names = langs.date_alias[lang]['months']['gentive']

        event_year = current_date.year

        list_of_elements = date_string.split()
        event_day = int(next(x for x in list_of_elements if x.isnumeric()))
        month_str = next(x for x in list_of_elements if x.isalpha())
        event_month = month_names.index(month_str) + 1

        # Case for the end of year: too old events are not in list
        # but there can be next year events pages in the last half of current year
        if (event_month-current_date.month) < -3:
            event_year += 1

        event_date = datetime.date(event_year, event_month, event_day)
        return event_date.isoformat()
    except StopIteration:
        return ''


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
    return list_of_descriptions


def themes(theme, page_data):
    bad_themes = ['Регистрация',
                  'Приветствие модератора',
                  'Вступительное слово',
                  'Начало регистрации',
                  'Общение',
                  'Заказываем пиццу и ставим оценки мероприятию']
    if not theme or theme in bad_themes:
        theme = ''
    return theme


def speakers(speaker, page_data):
    if speaker:
        return speaker
    else:
        return ''


def speakers_companies(speaker_company, page_data):
    if speaker_company:
        return speaker_company
    else:
        return ''


def price(price_string, page_data):
    free_strings = ['бесплатно', 'без оплаты']
    for _ in free_strings:
        if _ in price_string.lower():
            price_string = '0'
    return price_string


def find_spec(data, json_file_name):
    '''Если в заголовке, теме, описаниях есть определенные слова,
    назначаем соответствующий тег. Возвращает множество тегов.'''
    tags = set()
    title = data.title
    event_url = data.event_url
    description = data.description
    themes = [title, event_url]
    if description:
        themes += description
    if type(data.themes) == list:
        themes += data.themes
    text = ' '.join(themes)
    
    keys = eval(f'files.{json_file_name}')
    for key in keys:
        for tag in keys[key]:
            if tag.lower() in text.lower():
                tags.add(key)
    return tags


def event_type(event_type_string, page_data):
    tags = set()
    for key in files.event_types:
        for tag in files.event_types[key]:
            if tag.lower() in event_type_string.lower():
                tags.add(key)
    return ' '.join(tags)