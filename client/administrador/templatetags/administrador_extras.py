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


ETIQUETAS_CAMPOS = {
    'num': 'ID', 'folio': 'Folio', 'codigo': 'Código',
    'nombre': 'Nombre', 'descripcion': 'Descripción',
    'costo': 'Costo', 'costo_total': 'Costo total', 'tipo': 'Tipo',
    'activo': 'Activo', 'correo': 'Correo', 'telefono': 'Teléfono',
    'direccion_calle': 'Calle', 'direccion_numero': 'Número exterior',
    'direccion_colonia': 'Colonia', 'rfc': 'RFC',
    'numero_linea': 'Número de línea', 'area': 'Área',
    'estado_linea': 'Estado de la línea', 'etapa': 'Etapa',
    'linea_produccion': 'Línea de producción', 'cantidad': 'Cantidad',
    'fecha': 'Fecha', 'unidad': 'Unidad',
    'edo_flujo_merma': 'Estado de la merma', 'usuario': 'Usuario',
    'lote_material': 'Lote', 'componente': 'Componente',
    'tipo_merma': 'Tipo de merma', 'causa_raiz': 'Causa raíz',
    'estacion_trabajo': 'Estación de trabajo', 'orden_produccion': 'Orden de producción',
    'fecha_reporte': 'Fecha de reporte', 'cantidad_reportada': 'Cantidad reportada',
    'cantidad_recibida': 'Cantidad recibida', 'diferencia': 'Diferencia',
    'motivo_reporte': 'Motivo del reporte', 'usuario_reporte': 'Reportado por',
    'registro_merma': 'Merma relacionada', 'edo_discrepancia': 'Estado de la discrepancia',
    'fecha_resolucion': 'Fecha de resolución', 'motivo_resolucion': 'Motivo de resolución',
    'usuario_resolucion': 'Resuelto por', 'fecha_generacion': 'Fecha de generación',
    'hora_generacion': 'Hora de generación', 'fecha_atencion': 'Fecha de atención',
    'hora_atencion': 'Hora de atención', 'edo_solicitud': 'Estado de la solicitud',
    'usuario_atencion': 'Atendido por', 'fecha_determinacion': 'Fecha de dictamen',
    'fecha_ejecucion': 'Fecha de ejecución', 'cantidad_ejecutada': 'Cantidad ejecutada',
    'observaciones': 'Observaciones', 'sale_almacen': 'Sale de almacén',
    'llega_almacen': 'Llega a almacén', 'disposicion_final': 'Disposición final',
    'estado_disposicion': 'Estado de la disposición', 'username': 'Usuario (login)',
    'empleado': 'Empleado', 'rol': 'Rol', 'numero': 'Número de empleado',
    'emNombre': 'Nombre', 'emPrimerApell': 'Primer apellido',
    'emSegundoApell': 'Segundo apellido', 'fecha_nacimiento': 'Fecha de nacimiento',
    'fecha_ingreso': 'Fecha de ingreso', 'turno': 'Turno',
    'password_modificada': 'Contraseña modificada',
}


def _etiqueta(campo):
    if campo in ETIQUETAS_CAMPOS:
        return ETIQUETAS_CAMPOS[campo]
    return campo.replace('_', ' ').replace('em', '', 1).capitalize()


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
            f'<strong>{_etiqueta(k)}:</strong> {escape(str(v))}' for k, v in nuevo.items()
        ))

    id_campo = next((c for c in IDENTIFICADORES if c in nuevo), None)
    lineas = []
    if id_campo:
        lineas.append(f'<strong>{_etiqueta(id_campo)}:</strong> {escape(str(nuevo[id_campo]))}')

    cambios = []
    for campo, valor in nuevo.items():
        if campo == id_campo:
            continue
        if str(anterior.get(campo)) != str(valor):
            cambios.append(
                f'<strong>{_etiqueta(campo)}:</strong> '
                f'<del class="mx-text-muted">{escape(str(anterior.get(campo)))}</del> &rarr; '
                f'<b>{escape(str(valor))}</b>'
            )

    if 'nombre' in nuevo and id_campo != 'nombre' and 'nombre' not in [c for c in cambios if 'nombre' in c]:
        if str(anterior.get('nombre')) == str(nuevo.get('nombre')):
            lineas.append(f'<span class="mx-text-muted">nombre: {escape(str(nuevo["nombre"]))}</span>')

    if not cambios:
        cambios = ['<span class="mx-text-muted">Sin cambios en los campos.</span>']

    return mark_safe('<br>'.join(lineas + cambios))