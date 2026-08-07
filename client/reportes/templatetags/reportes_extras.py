from django import template

register = template.Library()

@register.filter
def moneda_mx(valor):
    """Formatea 808550.0 -> 808,550.00"""
    try:
        return f'{float(valor):,.2f}'
    except (ValueError, TypeError):
        return valor