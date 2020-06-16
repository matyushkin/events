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


def fields_order(name):
    result = {'start': [], 'event': [], 'analysis': []}
    for field in fields:
        for key in result.keys():
            type_ = pages[name][field]['page']
            if type_ == key:
                result[key].append(field)
    return result


def get_content(name, url, field):
    elements = fields[field]['elements']
    start_url = pages[name]['start_url']
    selectors = pages[name][field]['selectors']
    default = pages[name][field].get('default', '')
    soup = soups.get(url)
    overlaps, content = [], []

    for key in selectors:
        tag, attr, content_type = selectors[key]
        overlaps += soup.find_all(tag, {attr: key})
        if content_type == 'text':
            content += [overlap.text.strip() for overlap in overlaps]
        else:
            content += [overlap[content_type] for overlap in overlaps]
    else:
        pass

    if elements != 'all':
        content = content[:elements]

    if elements == 1:
        if len(content) == 0:
            content = '' or default
        if len(content) == 1:
            content = content[0]

    if elements == 'all':
        if len(content) == 0:
            content = [default]

    if url != start_url:
        try:
            content = eval(f'handlers.{field}(content, name)')
        except AttributeError as err:
            print(err)

    return content
