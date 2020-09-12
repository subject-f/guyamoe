import markdown
from django import template
from django.template.defaultfilters import stringfilter

from misc.models import Page

register = template.Library()


@register.filter()
@stringfilter
def convert_to_markdown(value):
    return markdown.markdown(value, extensions=["markdown.extensions.extra"])
