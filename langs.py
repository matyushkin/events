import re
import locale
import datetime
locale.setlocale(locale.LC_ALL, '')

import files

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
    return f'{date} в {time}'


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


def text_cleaner(text):
    bad = files.events_bad['combinations']
    for b in bad:
        variants = b, b.capitalize()
        for v in variants:
            # выделяем предложения, в которых есть искомые фразы
            pattern = re.compile(f"[^.!?;]*({v})[^.?!;]*[.?!;]")
            text = re.sub(pattern, '', text)        
    return text.strip()



def sentence_cleaner(text):
    '''Возвращает текст после удаления некорректных выражений'''
    bad_sentences = files.events_bad['sentences']
    paragraphs = text.split('\n')
    for p in paragraphs:
        if p.lower().strip() in bad_sentences:
            paragraphs.remove(p)
    return '\n'.join(paragraphs).strip()


def sentence_by_combination_cleaner(text):
    pattern = re.compile(r'.*?[\.\?!]')
    sentence_list = re.findall(pattern, text)
    bad_combinations = files.events_bad['combinations']
    for b in bad_combinations:
        for s in sentence_list:
            if b.lower() in s.lower():
                sentence_list.remove(s)
    return ''.join(sentence_list).strip()



def find_speakers_in_text(text):
    speakers = []
    patterns_strings = [r'(?<=Спикер – ).*?(?=[.])']

    for s in patterns_strings:
        pattern = re.compile(s)
        t = re.findall(pattern, text)
        if t:
            speakers += t
            break
    speakers = [speaker[0].upper() + speaker[1:] for speaker in speakers]
    return speakers


# r'(?<=[1-9]\) ).*(?=[ .;])*'
def find_themes_in_text(text):
    start_combinations = ["в программе вебинара",
                    "к обсуждению",
                    "которые мы затронем",
                    "вы узнаете",
                    "темы"]
    themes = []
    patterns_strings = [r'(?<=с докладом ["«]).*?(?=["»])',
                    r'(?<= – ).*?(?=[.;:])']

    for s in patterns_strings:
        pattern = re.compile(s)
        t = re.findall(pattern, text)
        if t:
            themes += t
            break
    themes = [theme[0].upper() + theme[1:] for theme in themes]
    return themes