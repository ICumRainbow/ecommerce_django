from django import template
import datetime

from django.utils.http import urlencode

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


@register.simple_tag(takes_context=True)
def append_to_url(context, value, field_name):
    url = context['request'].GET.copy()
    url[field_name] = value

    return '?' + url.urlencode()
