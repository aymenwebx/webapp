from django import template

register = template.Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None


@register.filter
def template_name(content_item):
    """
    Returns the appropriate template name for the content item
    """
    return f'courses/content/{content_item._meta.model_name}.html'