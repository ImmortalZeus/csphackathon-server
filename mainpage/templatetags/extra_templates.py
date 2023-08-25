from django import template
from ..models import Contestant

register = template.Library()

@register.simple_tag
def set(val=None):
    return val

@register.filter
def index(indexable, i):
    if i >= len(indexable):
        return indexable[0]
    else:
        return indexable[i]

@register.filter
def get_item(dictionary, key):
    key -= 1
    key = str(key)
    if key in dictionary :
        return dictionary[key]
    else:
        return None