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
    mapa = {'CREATE': 'Alta', 'INSERT': 'Alta', 'UPDATE': 'Modificación', 'DELETE': 'Baja'}
    return mapa.get(valor, valor)

IDENTIFICADORES = ('codigo', 'folio', 'numero_linea', 'numero', 'num')

def _parse_json(valor):
    if not valor or valor == 'None':
        return None
    try:
        datos = json.loads(valor)
    except (ValueError, TypeError):
        return None
    return datos if isinstance(datos, dict) else None


@register.filter
def diferencias_json(valor_anterior, valor_nuevo):
    """
    Compara valor_anterior vs valor_nuevo y muestra SOLO lo que cambió,
    con el identificador de la fila siempre visible arriba para dar contexto.
    - INSERT (no hay anterior): muestra el registro completo.
    - UPDATE: muestra el identificador + cada campo distinto, tachando el
      valor viejo y resaltando el nuevo.
    - Datos antiguos en texto plano (no JSON): se muestran tal cual, sin
      romper la tabla.
    """
    from django.utils.safestring import mark_safe
    from django.utils.html import escape

    nuevo = _parse_json(valor_nuevo)
    anterior = _parse_json(valor_anterior)

    if nuevo is None:
        texto = valor_nuevo or valor_anterior or ''
        return escape(texto)

    if anterior is None:
        return mark_safe('<br>'.join(
            f'<strong>{escape(k)}:</strong> {escape(str(v))}' for k, v in nuevo.items()
        ))

    id_campo = next((c for c in IDENTIFICADORES if c in nuevo), None)
    lineas = []
    if id_campo:
        lineas.append(f'<strong>{escape(id_campo)}:</strong> {escape(str(nuevo[id_campo]))}')

    cambios = []
    for campo, valor in nuevo.items():
        if campo == id_campo:
            continue
        if str(anterior.get(campo)) != str(valor):
            cambios.append(
                f'<strong>{escape(campo)}:</strong> '
                f'<del class="mx-text-muted">{escape(str(anterior.get(campo)))}</del> &rarr; '
                f'<b>{escape(str(valor))}</b>'
            )

    if 'nombre' in nuevo and id_campo != 'nombre' and 'nombre' not in [c for c in cambios if 'nombre' in c]:
        if str(anterior.get('nombre')) == str(nuevo.get('nombre')):
            lineas.append(f'<span class="mx-text-muted">nombre: {escape(str(nuevo["nombre"]))}</span>')

    if not cambios:
        cambios = ['<span class="mx-text-muted">Sin cambios en los campos.</span>']

    return mark_safe('<br>'.join(lineas + cambios))