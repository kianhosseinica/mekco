# custom_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0

@register.filter
def total_price(cart_items):
    try:
        return sum(item.quantity * item.price for item in cart_items)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return 0
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)