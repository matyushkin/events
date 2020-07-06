import locale
import datetime
locale.setlocale(locale.LC_ALL, '')

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