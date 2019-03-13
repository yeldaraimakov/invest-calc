from django import template

register = template.Library()


@register.filter
def index(List, i):
    return List[int(i)]


@register.simple_tag
def subtract(a, b):
    return a-b
