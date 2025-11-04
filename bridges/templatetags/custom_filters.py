from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another.
    Usage: {{ my_string | replace:"old,new" }}
    """
    if len(arg.split(',')) != 2:
        return value  # Return original if args are incorrect
        
    find_what, replace_with = arg.split(',')
    
    return value.replace(find_what.strip(), replace_with.strip())


@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    # Safely append the new classes
    value.field.widget.attrs['class'] = f"{css_classes} {arg}"
    return value