from django import template
from django.utils.translation import gettext


register = template.Library()

@register.inclusion_tag('form_errors.html')
def form_errors(form):
    return {'form': form}
