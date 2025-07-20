# church/templatetags/custom_filters.py
import calendar
from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def remove_auto_fetch_note(text):
    if not text:
        return ""
    return text.replace("Auto-fetched from Bible-API.com", "").strip()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_month_abbr(month_number):
    return calendar.month_abbr[int(month_number)]