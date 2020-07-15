import copy
import re
import locale
import datetime

locale.setlocale(locale.LC_ALL, '')

from bs4 import BeautifulSoup

import files
import urls

date_alias = {'rus':
                 {'weekdays':
                    {'short': ('пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс')},
                  'months':
                    {'gentive': ('января', 'февраля', 'марта',
                                 'апреля', 'мая', 'июня',
                                 'июля', 'августа', 'сентября',
                                 'октября', 'ноября', 'декабря'),
                    'nominative':('январь', 'февраль', 'март',
                                 'апрель', 'май', 'июнь',
                                 'июль', 'август', 'сентябрь',
                                 'октябрь', 'ноябрь', 'декабрь')}
                 }
              }

def make_datetime_string(date, time):
    date_dt = datetime.datetime.strptime(date,'%Y-%m-%d')
    date = date_dt.strftime('%a, %-d %B')
    if time:
        return f'{date} в {time}'
    else:
        return date


def month_names_for_time_filters():
    m = datetime.date.today().month-1
    month_names = date_alias['rus']['months']['nominative']
    month_names = [name.capitalize() for name in month_names]
    current_month_name = month_names[m]
    return month_names[m:]+month_names[:m]


def date_to_month(date_str:str):
    '''Получает строку даты в ISO формате. Если месяц в течение ближайшего года --
    возвращает название месяца. Если позже -- строку "Позже".'''
    
    if date_str:
        if date_str == 'infty':
            return '∞'
        else:
            today = datetime.date.today()
            first_date_later = datetime.date(today.year+1, today.month, 1)
            
            
            event_date = datetime.date.fromisoformat(date_str)

            
            if event_date >= first_date_later:
                return 'Позже'
            else:       
                months_names = date_alias['rus']['months']['nominative']
                month_number = event_date.month
                month_name = months_names[month_number-1]
                return month_name.capitalize()
    else:
        return ''


def is_first_program_str(s):
    res = re.findall(r'(?:направления|потоки|тайминг|программ|план(?!ирует)|узнае|теори|Что.*курсе\?|темы|доклады|сценарий)[\s\S]*?(?::|\?)\n?',
                   s, re.IGNORECASE)
    if res:
        return res[0]
    else:
        return None


def pop_themes_from_soup(soup, themes):
    ouls = soup.find_all(['ul', 'ol'])
    for oul in ouls:
        prev = oul.find_previous_sibling("p")
        if prev:
            s = str(prev)
            if is_first_program_str(s):
                new_themes = [li.text for li in oul.find_all('li')]
                new_themes = [re.sub('[;.,]$','', theme) for theme in new_themes]
                new_themes = [re.sub('\xa0', ' ', theme) for theme in new_themes]
                oul.extract()
                prev.extract()
                themes += new_themes
    if not ouls:
        tmp_html = str(soup)
        res = is_first_program_str(tmp_html)
        if res:
            new_themes = re.findall('(?:<br/>|</p>)[-–—✔️]\s[\s\S]*?\s*(?:<br/>|</p>)', tmp_html)
            tmp_html = tmp_html.replace(res, '')
            for theme in new_themes:
                tmp_html = tmp_html.replace(theme, '')
            themes += new_themes
        soup = BeautifulSoup(tmp_html, 'html.parser')
    # Очищаем мусорные символы вначале и в конце строк
    themes = [re.sub('^(?:<br/>|>|\n)*[-—–]*\s*', '', theme) for theme in themes]
    themes = [re.sub('[\.;,](?:<br/>)*(?:\\r)*(?:</p>|<br/>)*$', '', theme) for theme in themes]
    themes = [theme[0].upper() + theme[1:] for theme in themes]
    return soup, themes


def pop_urls_from_soup(soup, urls_list):
    links = soup.find_all('a')
    for link in links:
        urls_list += [urls.utm_cleaner(link['href'])]
    return soup, urls_list


def pop_timing_from_soup(soup, timing_str):
    for tag in soup.find_all(['p', 'li']):
        m = re.findall('(?:длительн|врем)[\s\S]*(?:минут|дн)[ыей]*',
                       tag.text, re.IGNORECASE)
        if m:
            timing_str = ''.join(m)
            break
    return soup, timing_str


def pop_speakers_from_text(text, speakers):
    m = re.search('(?:спикер|докладчи|стрим провед|вебинар провед)[\s\S]*',
                  text, re.IGNORECASE)
    if m:
        speaker_str = m.string[m.start():m.end()]
        # Патерн для Имя Фамилия
        speakers += re.findall('[А-Я]{1}[а-яё]{1,20} [А-Я]{1}[а-яё]{1,20}',
                   speaker_str)
        if speakers:
            text = text.replace(speaker_str, '')
    return text, speakers


def clean_text(text):
    text = re.sub('^\n?[\s\S]*(?:>|<br/>)\s*[-—–]*\s*', '', text)
    bad_c = files.bad['combinations']
    for b in bad_c:
        pattern = re.compile(f'.*?{b}.*?[\.\?!\n]', re.IGNORECASE)
        text = re.sub(pattern, '', text)
    return text


def soup_to_text(s):
    themes = []
    url_list = []
    timing_str = ''
    speakers = []
    s = copy.copy(s)
    s, themes = pop_themes_from_soup(s, themes)
    s, urls_list = pop_urls_from_soup(s, url_list)
    s, timing_str = pop_timing_from_soup(s, timing_str)
    t, speakers = pop_speakers_from_text(s.text, speakers)
    t = clean_text(t)
    return {'text': " ".join(t.split()),
            'themes':themes,
            'timing':timing_str,
            'speakers':speakers,
            'urls':urls_list}


def string_of_page_checked_urls(pages_checked):
    str_list = []
    for page in pages_checked:
        s = f'<a href="{page}">{files.pages_info[page]["name_gen"]}</a>'
        str_list.append(s)
    ps = ", ".join(str_list)
    ps = ' и'.join(ps.rsplit(",", 1))
    return ps


def date_interval_string(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    if start_date.year == end_date.year:
        return f"с {start_date.strftime('%-d %B')} по \
{end_date.strftime('%-d %B %Y')} года"
    else:
        return f"с {start_date.strftime('%-d %B %Y')} года по \
{end_date.strftime('%d %B %Y')} года"
