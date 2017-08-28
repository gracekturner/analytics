from django import template
register = template.Library()

@register.filter(name='texts')
def texts(settings):
    print settings
