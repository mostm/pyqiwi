# -*- coding: utf-8 -*-
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


def qiwi_date(date: datetime.datetime):
    return date.strftime("%Y-%m-%dT%H:%M:%S+03:00")


def stat_dates(start_date, end_date, params):
    if isinstance(start_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
        params['startDate'] = qiwi_date(start_date)
        params['endDate'] = qiwi_date(end_date)
    else:
        raise TypeError('You should use datetime.datetime Type for start_date and end_date')
    return params


def url_params(url):
    parsed_url = urlparse(url)
    params = {}
    for param in parsed_url.query.split('&'):
        try:
            params[param.split('=')[0]] = param.split('=')[1]
        except IndexError:
            params[param.split('=')[0]] = None
    return params

def split_float(amount: float):
    params = {}
    if type(amount) == float:
        params['amountInteger'] = str(amount).split('.')[0]
        params['amountFraction'] = str(amount).split('.')[1]
    else:
        params['amountInteger'] = amount
    return params

def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z
