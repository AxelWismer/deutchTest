from django import template

register = template.Library()

@register.filter
def is_string(obj):
    return isinstance(obj, str)
