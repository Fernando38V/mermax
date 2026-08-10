from django.shortcuts import render
from django.db.utils import OperationalError
# Create your views here.
"""
App: reportes - views

RF-11  Consulta de trazabilidad de lote
RF-12  Dashboard de indicadores (KPIs)
RF-13  Emisión de alertas automáticas
RF-14  Generación de reportes exportables a PDF

Nota sobre los KPIs: no se guardan en ninguna tabla, se calculan al vuelo
sobre REGISTRO_MERMA y TURNO_ORDEN. Guardarlos precalculados obligaría a
mantenerlos sincronizados con cada merma nueva, y el RF-12 pide que el panel
sea en tiempo real.
"""
from datetime import date, datetime
from django.db import connection
from django.db.models import Count, F, Sum
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogos.models import CausaRaiz, LineaProduccion
from inspecciones.models import RegistroDisposicion
from mermas.models import RegistroMerma, TurnoOrden
from recepciones.models import LoteMaterial

from . import serializers as s
from .models import AlertaGenerada, UmbralAlerta

# Estados que ya no cuentan como scrap "vivo" no existen: toda merma
# registrada cuenta para el KPI, sin importar en qué punto del flujo esté.
# Sólo se excluyen las que quedaron bloqueadas por discrepancia, porque su
# cantidad todavía está en disputa.
ESTADOS_EN_DISPUTA = ['DISCREPAN']


# ======================================================
# Permisos
# ======================================================

class SoloCalidadOAdmin(permissions.BasePermission):
    """RF-13: las alertas se despliegan y se atienden en el panel de Calidad."""
    message = 'Sólo el Ingeniero de Calidad puede atender alertas.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.rol_id in ('CALID', 'ADMIN')


# ======================================================
# Utilidades de rango de fechas
# ======================================================

def _rango(request):
    """
    Lee ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD. Si no vienen, no filtra.
    Devuelve (desde, hasta) como date o None.
    """
    def parsear(nombre):
        valor = request.query_params.get(nombre)
        if not valor:
            return None
        try:
            return datetime.strptime(valor, '%Y-%m-%d').date()
        except ValueError:
            return None

    return parsear('desde'), parsear('hasta')


def _filtrar_por_fecha(qs, desde, hasta, campo='fecha'):
    if desde:
        qs = qs.filter(**{f'{campo}__gte': desde})
    if hasta:
        qs = qs.filter(**{f'{campo}__lte': hasta})
    return qs


# ======================================================
# RF-12: Dashboard de indicadores
# ======================================================

class DashboardView(APIView):
    """
    GET /api/reportes/dashboard/?desde=&hasta=

    Devuelve el panel completo del RF-12:
      - porcentaje de scrap por línea con semáforo
      - ranking de causas raíz más frecuentes
      - impacto económico del período
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        desde, hasta = _rango(request)

        lineas = self._kpi_por_linea(desde, hasta)
        causas = self._ranking_causas(desde, hasta)

        mermas = _filtrar_por_fecha(RegistroMerma.objects.all(), desde, hasta)
        totales = mermas.aggregate(
            eventos=Count('folio'),
            piezas=Sum('cantidad'),
            costo=Sum('costo_total'),
        )

        return Response({
            'periodo': {'desde': desde, 'hasta': hasta},
            'resumen': {
                'eventos': totales['eventos'] or 0,
                'piezas_mermadas': float(totales['piezas'] or 0),
                'impacto_economico': totales['costo'] or 0,
                'lineas_en_alerta': sum(1 for l in lineas if l['semaforo'] == 'rojo'),
            },
            'por_linea': s.LineaKpiSerializer(lineas, many=True).data,
            'causas_raiz': s.CausaRaizKpiSerializer(causas, many=True).data,
        })

    # --- cálculo ---------------------------------------------------------

    def _kpi_por_linea(self, desde, hasta):
        # Producción: TURNO_ORDEN -> ORDEN_PRODUCCION -> ESTACION -> LINEA
        produccion = {}
        qs_prod = _filtrar_por_fecha(
            TurnoOrden.objects.select_related('orden_produccion__estacion_trabajo'),
            desde, hasta,
        )
        for to in qs_prod:
            linea_id = to.orden_produccion.estacion_trabajo.linea_produccion_id
            produccion[linea_id] = produccion.get(linea_id, 0) + (to.cantidad_producida or 0)

        # Merma: REGISTRO_MERMA -> ESTACION -> LINEA
        merma_piezas, merma_costo = {}, {}
        qs_merma = _filtrar_por_fecha(
            RegistroMerma.objects
            .select_related('estacion_trabajo')
            .exclude(estacion_trabajo__isnull=True)
            .exclude(edo_flujo_merma__in=ESTADOS_EN_DISPUTA),
            desde, hasta,
        )
        for m in qs_merma:
            linea_id = m.estacion_trabajo.linea_produccion_id
            merma_piezas[linea_id] = merma_piezas.get(linea_id, 0) + float(m.cantidad)
            merma_costo[linea_id] = merma_costo.get(linea_id, 0) + float(m.costo_total or 0)

        # Umbrales configurados de porcentaje de scrap
        umbrales = {
            u.linea_produccion_id: float(u.valor)
            for u in UmbralAlerta.objects.filter(indicador_kpi='PCT_SCRAP', activo=True)
        }

        filas = []
        for linea in LineaProduccion.objects.order_by('numero_linea'):
            # Usar la clave primaria de la línea para buscar en los diccionarios
            linea_key = linea.pk

            producidas = produccion.get(linea_key, 0)
            mermadas = merma_piezas.get(linea_key, 0)

            # --- CORRECCIÓN DE LÓGICA SCRAP ---
            if producidas > 0:
                pct = (mermadas / producidas) * 100
            elif mermadas > 0:
                # Si hay mermas pero 0 unidades producidas, la merma es del 100% (Crítico)
                pct = 100.0
            else:
                pct = 0.0

            umbral = umbrales.get(linea_key)

            filas.append({
                'linea': linea.num,
                'linea_nombre': linea.nombre,
                'piezas_producidas': producidas,
                'piezas_mermadas': round(mermadas, 2),
                'porcentaje_scrap': round(pct, 2),
                'costo_scrap': round(merma_costo.get(linea_key, 0), 2),
                'umbral': umbral,
                'semaforo': self._semaforo(pct, umbral),
            })
        return filas

    @staticmethod
    def _semaforo(pct, umbral):
        """
        RNF-07: rojo, amarillo y verde. Se usa el 80% del umbral como aviso
        temprano, para que la línea no pase de verde a rojo sin transición.
        """
        if umbral is None:
            return 'sin_umbral'
        if pct >= umbral:
            return 'rojo'
        if pct >= umbral * 0.8:
            return 'amarillo'
        return 'verde'

    def _ranking_causas(self, desde, hasta):
        qs = _filtrar_por_fecha(
            RegistroMerma.objects.exclude(causa_raiz__isnull=True), desde, hasta,
        )
        agregado = (qs.values('causa_raiz')
                      .annotate(eventos=Count('folio'),
                                piezas=Sum('cantidad'),
                                costo=Sum('costo_total'))
                      .order_by('-eventos'))

        nombres = dict(CausaRaiz.objects.values_list('codigo', 'nombre'))
        return [{
            'causa_raiz': f['causa_raiz'],
            'nombre': nombres.get(f['causa_raiz'], f['causa_raiz']),
            'eventos': f['eventos'],
            'piezas': float(f['piezas'] or 0),
            'costo': f['costo'] or 0,
        } for f in agregado]


# ======================================================
# RF-11: Trazabilidad de lote
# ======================================================

class TrazabilidadLoteView(APIView):
    """
    GET /api/reportes/trazabilidad/lote/<num>/

    Ciclo completo de un lote: cuánto entró, cuánto se convirtió en scrap,
    cuánto se aprovechó, qué disposición se le dio y cuánto costó el
    desperdicio.

    El cálculo numérico (cantidad mermada, % de merma, costo del
    desperdicio) vive en el procedimiento almacenado sp_trazabilidad_lote;
    esta vista solo agrega los datos descriptivos del lote (proveedor,
    componente) y el desglose de disposición final, que el SP no cubre.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, num):
        lote = (LoteMaterial.objects
                .select_related('componente', 'proveedor')
                .filter(num=num).first())
        if lote is None:
            return Response({'detail': 'Lote no encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

        with connection.cursor() as cursor:
            try:
                cursor.callproc('sp_trazabilidad_lote', [num])
                fila = cursor.fetchone()
            except OperationalError as e:
                mensaje = str(e.args[1]) if len(e.args) > 1 else str(e)
                return Response({'detail': mensaje}, status=status.HTTP_400_BAD_REQUEST)

        # fila = (numLote, cantidadRecibida, cantidadMermada, porcentajeMerma,
        #          costoTotalDesperdicio, eventosMerma), en ese orden exacto
        # según el SELECT final de sp_trazabilidad_lote.
        recibidas = float(fila[1])
        mermadas = float(fila[2])

        resumen = {
            'lote': lote.num,
            'numero_lote_proveedor': lote.numero_lote_prov,
            'componente': lote.componente_id,
            'componente_nombre': lote.componente.nombre,
            'proveedor': lote.proveedor.nombre,
            'fecha_recepcion': lote.fecha,
            'cantidad_recibida': recibidas,
            'cantidad_mermada': mermadas,
            'cantidad_aprovechada': round(recibidas - mermadas, 2),
            'porcentaje_merma': float(fila[3]),
            'costo_desperdicio': fila[4],
        }

        disposiciones = (RegistroDisposicion.objects
                         .filter(registro_merma__lote_material=lote)
                         .values('disposicion_final')
                         .annotate(eventos=Count('folio'),
                                   cantidad=Sum('cantidad_ejecutada'))
                         .order_by('-eventos'))

        return Response({
            'resumen': s.TrazabilidadLoteSerializer(resumen).data,
            'eventos_merma': fila[5],
            'disposicion_final': [
                {'dictamen': d['disposicion_final'],
                 'eventos': d['eventos'],
                 'cantidad': float(d['cantidad'] or 0)}
                for d in disposiciones
            ],
        })


# ======================================================
# RF-13: Alertas automáticas
# ======================================================

class EvaluarAlertasView(APIView):
    """
    POST /api/reportes/alertas/evaluar/

    Recorre los umbrales activos, calcula el indicador correspondiente y
    genera una alerta por cada umbral rebasado.

    No duplica: si ya existe una alerta ACTIVA para ese umbral, la deja como
    está. El RF-13 dice que la alerta bloquea su estado hasta ser atendida,
    así que reabrirla en cada evaluación la volvería inútil.
    """
    permission_classes = [SoloCalidadOAdmin]

    def post(self, request):
        generadas, ya_activas = [], 0

        for umbral in (UmbralAlerta.objects
                       .filter(activo=True)
                       .select_related('linea_produccion', 'indicador_kpi')):

            valor = self._calcular(umbral)
            if valor is None or valor < float(umbral.valor):
                continue

            if AlertaGenerada.objects.filter(umbral_alerta=umbral,
                                             estado_alerta='ACTIVA').exists():
                ya_activas += 1
                continue

            alerta = AlertaGenerada.objects.create(
                fecha=date.today(),
                valor_detectado=round(valor, 2),
                estado_alerta_id='ACTIVA',
                umbral_alerta=umbral,
                usuario=None,
            )
            generadas.append(alerta)

        return Response({
            'generadas': len(generadas),
            'ya_activas': ya_activas,
            'alertas': s.AlertaGeneradaSerializer(generadas, many=True).data,
        }, status=status.HTTP_201_CREATED if generadas else status.HTTP_200_OK)

    def _calcular(self, umbral):
        """Devuelve el valor actual del indicador de ese umbral."""
        linea = umbral.linea_produccion_id

        mermas = (RegistroMerma.objects
                  .select_related('estacion_trabajo')
                  .filter(estacion_trabajo__linea_produccion=linea)
                  .exclude(edo_flujo_merma__in=ESTADOS_EN_DISPUTA))

        if umbral.indicador_kpi_id == 'COSTO_MERMA':
            return float(mermas.aggregate(c=Sum('costo_total'))['c'] or 0)

        if umbral.indicador_kpi_id == 'PCT_SCRAP':
            mermadas = float(mermas.aggregate(p=Sum('cantidad'))['p'] or 0)
            producidas = (TurnoOrden.objects
                          .filter(orden_produccion__estacion_trabajo__linea_produccion=linea)
                          .aggregate(p=Sum('cantidad_producida'))['p'] or 0)
            return (mermadas / producidas * 100) if producidas else None

        # TOP_CAUSA y cualquier KPI futuro que no sea de umbral numérico
        return None


class AlertaListView(APIView):
    """GET /api/reportes/alertas/?estado=ACTIVA"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = (AlertaGenerada.objects
              .select_related('umbral_alerta__linea_produccion',
                              'umbral_alerta__indicador_kpi',
                              'estado_alerta', 'usuario')
              .order_by('-fecha', '-num'))

        estado = request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado_alerta=estado.upper())

        return Response(s.AlertaGeneradaSerializer(qs, many=True).data)


class AtenderAlertaView(APIView):
    """
    POST /api/reportes/alertas/<num>/atender/  {"observaciones": "..."}

    RF-13: la alerta permanece bloqueada hasta ser cerrada con una
    observación. Aquí se registra quién la atendió y qué hizo.
    """
    permission_classes = [SoloCalidadOAdmin]

    def post(self, request, num):
        alerta = AlertaGenerada.objects.filter(num=num).first()
        if alerta is None:
            return Response({'detail': 'Alerta no encontrada.'},
                            status=status.HTTP_404_NOT_FOUND)

        if alerta.estado_alerta_id == 'ATENDIDA':
            return Response({'detail': 'Esta alerta ya fue atendida.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = s.AtenderAlertaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        alerta.observaciones = serializer.validated_data['observaciones']
        alerta.estado_alerta_id = 'ATENDIDA'
        alerta.usuario = request.user
        alerta.save(update_fields=['observaciones', 'estado_alerta', 'usuario'])

        return Response(s.AlertaGeneradaSerializer(alerta).data)


class UmbralListView(APIView):
    """
    GET /api/reportes/umbrales/ — Muestra los umbrales configurados.
    POST /api/reportes/umbrales/ — Crea o actualiza (Upsert) el umbral de una línea.
    """
    permission_classes = [SoloCalidadOAdmin]

    def get(self, request):
        qs = (UmbralAlerta.objects
              .select_related('linea_produccion', 'indicador_kpi')
              .order_by('linea_produccion__numero_linea'))
        return Response(s.UmbralAlertaSerializer(qs, many=True).data)

    def post(self, request):
        """
        RF-13 / RF-15: Configura el porcentaje o cantidad máxima permitida.
        Body: { "linea_produccion": 1, "indicador_kpi": "PCT_SCRAP", "valor": 5.0, "activo": true }
        """
        linea_id = request.data.get('linea_produccion')
        indicador_id = request.data.get('indicador_kpi', 'PCT_SCRAP')
        valor = request.data.get('valor')
        activo = request.data.get('activo', True)

        if not linea_id or valor is None:
            return Response(
                {'detail': 'Se requiere la línea de producción y el valor del umbral.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        umbral, created = UmbralAlerta.objects.update_or_create(
            linea_produccion_id=linea_id,
            indicador_kpi_id=indicador_id,
            defaults={'valor': valor, 'activo': activo}
        )

        return Response(
            s.UmbralAlertaSerializer(umbral).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


# ======================================================
# RF-14: Reporte detallado y exportación
# ======================================================

def _construir_reporte(request):
    """
    Aplica los filtros del RF-14: línea, turno, tipo de merma, causa raíz y
    rango de fechas. Devuelve (filas, filtros_aplicados).
    """
    desde, hasta = _rango(request)

    qs = (RegistroMerma.objects
          .select_related('estacion_trabajo__linea_produccion', 'componente',
                          'tipo_merma', 'causa_raiz', 'edo_flujo_merma',
                          'orden_produccion')
          .order_by('-fecha', 'folio'))

    qs = _filtrar_por_fecha(qs, desde, hasta)

    filtros = {'desde': str(desde) if desde else None,
               'hasta': str(hasta) if hasta else None}

    linea = request.query_params.get('linea')
    if linea:
        qs = qs.filter(estacion_trabajo__linea_produccion=linea)
        filtros['linea'] = linea

    tipo = request.query_params.get('tipo_merma')
    if tipo:
        qs = qs.filter(tipo_merma=tipo.upper())
        filtros['tipo_merma'] = tipo.upper()

    causa = request.query_params.get('causa_raiz')
    if causa:
        qs = qs.filter(causa_raiz=causa.upper())
        filtros['causa_raiz'] = causa.upper()

    # El turno no está en REGISTRO_MERMA: se llega por la orden de producción
    turno = request.query_params.get('turno')
    if turno:
        qs = qs.filter(orden_produccion__turnoorden__turno=turno.upper()).distinct()
        filtros['turno'] = turno.upper()

    # Dictamen aplicado, si ya lo tiene
    dictamenes = dict(
        RegistroDisposicion.objects.values_list('registro_merma_id', 'disposicion_final_id')
    )
    turnos_por_orden = {}
    for to in TurnoOrden.objects.all():
        turnos_por_orden.setdefault(to.orden_produccion_id, to.turno_id)

    filas = [{
        'folio': m.folio,
        'fecha': m.fecha,
        'linea': m.estacion_trabajo.linea_produccion.nombre if m.estacion_trabajo else '',
        'estacion': m.estacion_trabajo.nombre if m.estacion_trabajo else '',
        'turno': turnos_por_orden.get(m.orden_produccion_id),
        'componente': m.componente.nombre if m.componente else '',
        'cantidad': float(m.cantidad),
        'costo_total': m.costo_total,
        'tipo_merma': m.tipo_merma.nombre if m.tipo_merma else None,
        'causa_raiz': m.causa_raiz.nombre if m.causa_raiz else None,
        'estado': m.edo_flujo_merma.nombre,
        'dictamen': dictamenes.get(m.folio),
    } for m in qs]

    return filas, filtros


class ReporteMermasView(APIView):
    """
    GET /api/reportes/mermas/?linea=&turno=&tipo_merma=&causa_raiz=&desde=&hasta=
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        filas, filtros = _construir_reporte(request)
        total_costo = sum(float(f['costo_total'] or 0) for f in filas)
        total_piezas = sum(f['cantidad'] for f in filas)

        return Response({
            'filtros': filtros,
            'totales': {
                'eventos': len(filas),
                'piezas': round(total_piezas, 2),
                'costo': round(total_costo, 2),
            },
            'resultados': s.MermaReporteSerializer(filas, many=True).data,
        })


class ReporteMermasPDFView(APIView):
    """
    GET /api/reportes/mermas/pdf/  con los mismos filtros.

    RNF-05: la generación no debe exceder 10 segundos. Se usa reportlab, que
    es Python puro y no depende de binarios externos; hay que instalarlo:
        pip install reportlab
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            )
        except ImportError:
            return Response(
                {'detail': 'Falta la librería reportlab. Instálala con: pip install reportlab'},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        filas, filtros = _construir_reporte(request)

        respuesta = HttpResponse(content_type='application/pdf')
        nombre = f'reporte_mermas_{date.today().isoformat()}.pdf'
        respuesta['Content-Disposition'] = f'attachment; filename="{nombre}"'

        doc = SimpleDocTemplate(
            respuesta, pagesize=landscape(letter),
            leftMargin=1.2 * cm, rightMargin=1.2 * cm,
            topMargin=1.2 * cm, bottomMargin=1.2 * cm,
            title='Reporte de mermas - Mermax',
        )
        estilos = getSampleStyleSheet()
        elementos = []

        elementos.append(Paragraph('Telvix Electronics S.A. de C.V.', estilos['Title']))
        elementos.append(Paragraph('Reporte de mermas y scrap', estilos['Heading2']))

        activos = [f'{k}: {v}' for k, v in filtros.items() if v]
        elementos.append(Paragraph(
            'Filtros aplicados: ' + (', '.join(activos) if activos else 'ninguno'),
            estilos['Normal'],
        ))
        elementos.append(Paragraph(
            f'Generado el {date.today().strftime("%d/%m/%Y")} por {request.user.username}',
            estilos['Normal'],
        ))
        elementos.append(Spacer(1, 0.5 * cm))

        encabezado = ['Folio', 'Fecha', 'Línea', 'Estación', 'Turno',
                      'Componente', 'Cant.', 'Costo', 'Causa raíz', 'Estado']
        datos = [encabezado]
        for f in filas:
            datos.append([
                f['folio'],
                f['fecha'].strftime('%d/%m/%Y'),
                f['linea'][:22],
                f['estacion'][:20],
                f['turno'] or '-',
                f['componente'][:22],
                f'{f["cantidad"]:.0f}',
                f'${float(f["costo_total"] or 0):,.2f}',
                (f['causa_raiz'] or '-')[:20],
                f['estado'],
            ])

        tabla = Table(datos, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (6, 1), (7, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#b0b0b0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f5f8')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elementos.append(tabla)

        total_costo = sum(float(f['costo_total'] or 0) for f in filas)
        total_piezas = sum(f['cantidad'] for f in filas)
        elementos.append(Spacer(1, 0.5 * cm))
        elementos.append(Paragraph(
            f'<b>Total:</b> {len(filas)} eventos · {total_piezas:.0f} piezas · '
            f'${total_costo:,.2f} de impacto económico',
            estilos['Normal'],
        ))

        doc.build(elementos)
        return respuesta