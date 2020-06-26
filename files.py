import json
import handlers
import soups

# all start pages
with open('files/pages.json') as pages_file:
    pages = json.load(pages_file)

# main events dict-type structure
with open('files/events.json') as events_file:
    events = json.load(events_file)

# basic characteristic of common fields
with open('files/fields.json') as fields_file:
    fields = json.load(fields_file)

# keywords for tag recognition
with open('files/tags.json') as tags_file:
    tags = json.load(tags_file)

# cities where events are registered
with open('files/cities.txt') as cities_file:
    cities = cities_file.read().split('\n')


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
    default = start_page_data[field].get('default', '')
    event_url = page_data.get('event_url'):
    if event_url:
        soup = soups.get(event_url)
    else:
        soup = soups.get(start_url)
    overlaps = []
    content = []

    try:
        for key in selectors:
            tag, attr, content_type = selectors[key]
            overlaps += soup.find_all(tag, {attr: key})
            if content_type == 'text':
                content += [overlap.text.strip() for overlap in overlaps]
            else:
                content += [overlap[content_type] for overlap in overlaps]

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

    return content
