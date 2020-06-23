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
                                 'октября', 'ноября', 'декабря')}
                 }
              }

def make_datetime_string(date, time):
	date_dt = datetime.datetime.strptime(date,'%Y-%m-%d')
	date = date_dt.strftime('%a, %-d %B')
	return f'{date} в {time}'
