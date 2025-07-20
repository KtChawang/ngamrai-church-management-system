from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """
    Safely gets value from a dictionary using key.
    """
    if isinstance(d, dict):
        return d.get(key, 0)
    return 0

@register.filter(name='index')
def index(sequence, position):
    """
    Safely gets item at index from a list/tuple.
    """
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return ''

@register.filter
def sum_list(value):
    """
    Safely sums a list or dict of numbers.
    Returns 0 if input is not valid or empty.
    """
    if isinstance(value, dict):
        return sum(v for v in value.values() if isinstance(v, (int, float)))
    elif isinstance(value, list):
        return sum(v for v in value if isinstance(v, (int, float)))
    return 0

@register.filter
def get_item(dictionary, key):
    """
    Allows use of 'dict|get_item:key' in templates for safe access.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0
