import datetime
from urllib.parse import urlparse


def sources_list(sources, params):
    """
    Adds defined list of sources to params

    Parameters
    ----------
    sources : list
        Payment sources
    params : dict
        Default params

    Returns
    -------
    dict
        params with sources
    """
    if isinstance(sources, list):
        for source in sources:
            params['sources[{0}]'.format(sources.index(source))] = source
    else:
        raise TypeError('You should use list Type for sources')
    return params


def stat_dates(start_date, end_date, params):
    if isinstance(start_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
        params['startDate'] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        params['endDate'] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        raise TypeError('You should use datetime.datetime Type for start_date and end_date')
    return params


def url_params(url):
    parsed_url = urlparse(url)
    params = {}
    for param in parsed_url.query.split('&'):
        params[param.split('=')[0]] = param.split('=')[1]
    return params
