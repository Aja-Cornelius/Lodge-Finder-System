from django import template
import re

register = template.Library()

@register.filter
def phone_clean(value):
    """Remove everything except digits from phone number and ensure it starts with 234"""
    if not value:
        return ''
    # Remove all non-digits
    digits = re.sub(r'\D', '', str(value))
    # If starts with 0, replace with 234
    if digits.startswith('0'):
        digits = '234' + digits[1:]
    # If doesn't start with 234 and is 10 digits, add 234
    elif len(digits) == 10:
        digits = '234' + digits
    return digits