import json

# custom packages
import files
import soups
import urls
import langs
import handlers

# Узнаем, какие из стартовых страниц, перечисленных в files.pages, размечены.
# Такие страницы содержат все поля, перечисленные в files.fields.
# Выводим список с помощью специальной функции pages_checked()

pages_checked = files.pages_checked()

# Для обработки полей, описывающих события, логична следующая последовательность:
# - cчитываемые поля со стартовой страницы (обычно это заголовк, дата, статус)
# - поля, расположенные на странице мероприятия (темы, докладчики, время начала)
# - получаемые из анализа предобработанных полей (теги, призы)


class StartPage:
    """Парсинг начальных страниц, описанных в pages.json"""
    def __init__(self, start_url):
        self.data, self.event_lists, self.events = {}, {}, {}
        self.data['start_url'] = start_url
        self.fields = files.fields_order(start_url)
        self.not_actual_events = set()
        for field in self.fields['start']:
            self.event_lists[field] = files.get_content(self.data, field, force=True)
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
    def __init__(self, event_url, start_page, force=False):
        self.data = start_page.events[event_url]
        self.data['start_url'] = start_page.data['start_url']
        self.data['event_url'] = event_url
        for field in start_page.fields['event']:
            self.data[field] = files.get_content(self.data, field, force)
            


for start_url in pages_checked:
    start_page = StartPage(start_url)
    actual = start_page.actual_events
    print(actual)
    for event_url in actual:
        event = EventPage(event_url, start_page)
        files.events[event_url] = event.data
    soups.del_not_actual(actual, start_page.data)