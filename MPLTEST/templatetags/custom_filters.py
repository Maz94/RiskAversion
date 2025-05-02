from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(obj, attr):
    """Lookup the attribute 'attr' on the given object 'obj'."""
    return getattr(obj, attr, '')


register = template.Library()

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return None
