from typing import Optional

from django import template
import datetime

register = template.Library()


@register.filter
def format_to_class_name(value):
    value = ''.join(filter(str.isalnum, value))
    return value


@register.filter
def subdivide(list_: list, args: str):
    """
    groups
    """
    args = args.split(',')
    stop = int(args[0])
    step = int(args[1]) if len(args) > 1 else 1
    list_ = list_[::step]
    result = [list_[i:i + stop] for i in range(0, len(list_), stop)]
    return result


@register.simple_tag
def format_date(value: datetime, time=False):
    if time:
        value = value.strftime("%B %d, %Y, %H:%M:%S")
    else:
        value = value.strftime("%B %d, %Y")
    return value


@register.simple_tag
def my_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)

    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)

    return url
