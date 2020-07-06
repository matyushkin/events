import json
import handlers
import soups

# all start pages and fields for such type of start and event pages
with open('files/pages_fields.json') as pages_file:
    pages = json.load(pages_file)

with open('files/pages_info.json') as pages_info_file:
    pages_info = json.load(pages_info_file)

# main events dict-type structure
with open('files/events.json') as events_file:
    events = json.load(events_file)

# basic characteristic of common fields
with open('files/fields.json') as fields_file:
    fields = json.load(fields_file)

# keywords for tag recognition
with open('files/tags.json') as tags_file:
    tags = json.load(tags_file)

# keywords for types recognition
with open('files/event_types.json') as event_types_file:
    event_types = json.load(event_types_file)

# cities where events are registered
with open('files/cities.txt') as cities_file:
    cities = cities_file.read().split('\n')

# events that don't correspond to current parser possibilities
with open('files/events_special.json') as special_file:
    events_special = json.load(special_file)

# events that I want to be promoted
with open('files/events_promo.json') as promo_file:
    events_promo = json.load(promo_file)

# events that I don't like
with open('files/events_bad.json') as bad_file:
    events_bad = json.load(bad_file)


def pages_checked():
    '''Check if all meta_fields are represented for page'''
    result = []
    meta_fields = set(fields.keys())
    for page in pages:
        page_fields = {field for field in pages[page]}
        if not (meta_fields - page_fields):
            result.append(page)
    return result


def fields_order(start_url):
    result = {'start': [], 'event': [], 'analysis': []}
    page_fields = {key for key in pages[start_url]}
    for field in page_fields:
        for key in result.keys():
            if pages[start_url][field]['page'] == key:
                result[key].append(field)
    return result


def get_content(page_data, field):
    start_url = page_data['start_url']
    start_page_data = pages[start_url]
    elements = start_page_data[field]['elements']
    selectors = start_page_data[field]['selectors']
    excluding_selectors = start_page_data[field].get('excluding_selectors', None)
    default = start_page_data[field].get('default', '')
    event_url = page_data.get('event_url')
    url = event_url if event_url else start_url
    soup = soups.get(url, start_url)
    overlaps, ex_overlaps = [], []
    content = []

    try:
        #print('FIELD', field)
        # Собираем информацию из селекторов, убираем лишние селекторы
        for key in selectors:
            tag, attr, content_type = selectors[key]
            overlaps += soup.find_all(tag, {attr: key})
        if excluding_selectors is not None:
            for ex_key in excluding_selectors:
                ex_tag, ex_attr = excluding_selectors[ex_key]
                ex_overlaps += soup.find_all(ex_tag, {ex_attr: ex_key})
        for _ in ex_overlaps:
            overlaps.remove(_)
        
        for overlap in overlaps:
            if content_type == 'text':
                content.append(overlap.text.strip())
            else:
                content.append(overlap[content_type])

        if elements == 1:
            if len(content) == 0:
                content = '' or default
            if len(content) >= 1:
                content = content[0]
            content = eval(f'handlers.{field}(content, page_data)')
        elif elements == 'all':
            if len(content) == 0:
                content = [default]
            new_content = []
            for c in content:
                new_content.append(eval(f'handlers.{field}(c, page_data)'))
            content = new_content
    
    except AttributeError as err:
        print(err)

    #print(url, field, content)
    return content
