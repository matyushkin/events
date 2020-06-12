def utm_cleaner(url):
    '''Deletes utm tags from url'''
    index = url.find('?utm')
    if index > 0:
        url = url[:index]
    return url


def add_home(event_url, start_url):
    ''' Sometimes urls has relative paths'''
    if 'http' not in event_url:
        event_url = start_url[:-1] + event_url
    return(event_url)