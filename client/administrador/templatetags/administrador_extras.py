import json
from datetime import datetime

from datetime import datetime
from zoneinfo import ZoneInfo

from django import template
register = template.Library()

@register.filter
def dictkey(d, key):
    if isinstance(d, dict):
        return d.get(key, '')
    return getattr(d, key, '')

@register.filter
def formatear_json(valor):
    if not valor or valor == 'None':
        return ''
    try:
        datos = json.loads(valor)
    except (ValueError, TypeError):
        return valor
    if not isinstance(datos, dict):
        return valor
    from django.utils.safestring import mark_safe
    return mark_safe('<br>'.join(f'<strong>{k}:</strong> {v}' for k, v in datos.items()))

@register.filter
def espaciar(valor):
    if valor is None:
        return valor
    return str(valor).replace('_', ' ')


@register.filter
def fecha_legible(valor):
    if not valor:
        return ''
    try:
        dt = datetime.fromisoformat(str(valor).replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except (ValueError, TypeError):
        return valor

@register.filter
def fecha_legible(valor):
    if not valor:
        return ''
    try:
        dt_utc = datetime.fromisoformat(str(valor).replace('Z', '+00:00'))
        dt_tijuana = dt_utc.astimezone(ZoneInfo('America/Tijuana'))
        return dt_tijuana.strftime('%d/%m/%Y %H:%M:%S')
    except (ValueError, TypeError):
        return valor

@register.filter
def traducir_accion(valor):
    mapa = {'CREATE': 'Alta', 'UPDATE': 'Modificación', 'DELETE': 'Baja'}
    return mapa.get(valor, valor)