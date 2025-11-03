# custom_filters.py
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Permite acceder a un valor de diccionario usando una clave en el template."""
    return dictionary.get(key)
