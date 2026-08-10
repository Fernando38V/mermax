from django.shortcuts import render, get_object_or_404

# Create your views here.
from auditoria.services import AuditoriaSqlMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from django.db import IntegrityError, DatabaseError, transaction, connection
from django.db.utils import OperationalError
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum
from datetime import date, timedelta
from .models import RegistroMerma

from catalogos.models import EstacionTrabajo
from catalogos.serializers import EstacionTrabajoSerializer
from mermas import serializers, models
from recepciones.models import LoteMaterial
from usuarios.permissions import (
    EsAlmacenista,
    LecturaTodosEscrituraAlmacenista,
    LecturaTodosEscrituraSupervisor,
)

# ======================================================
# Paginacion
# ======================================================

class MermasPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# ======================================================
# Registro de Merma
# ======================================================

class ListRegistroMermaAPIView(generics.ListAPIView):
    permission_classes = [LecturaTodosEscrituraSupervisor]
    serializer_class = serializers.ListRegistroMermaSerializer
    pagination_class = MermasPagination
    
    def get_queryset(self):
        queryset = models.RegistroMerma.objects.all()
        params = self.request.query_params
        
        linea = params.get('linea')
        tipo = params.get('tipo_merma')
        componente = params.get('componente')
        estado = self.request.query_params.get("estado")
        fecha = self.request.query_params.get("fecha")
        
        if linea:
            queryset = queryset.filter(estacion_trabajo__linea_produccion=linea)

        if tipo:
            queryset = queryset.filter(tipo_merma=tipo)

        if componente:
            queryset = queryset.filter(componente=componente)

        if estado:
            queryset = queryset.filter(edo_flujo_merma=estado)

        if fecha:
            queryset = queryset.filter(fecha=fecha)
            
        return queryset.order_by('-fecha', '-folio')
        
class CreateRegistroMermaAPIView(AuditoriaSqlMixin, generics.CreateAPIView):
    permission_classes = [LecturaTodosEscrituraSupervisor]
    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.CreateRegistroMermaSerializer

    def perform_create(self, serializer):
        serializer.save(
            usuario=self.request.user,
            edo_flujo_merma_id='REGISTRADA')


class DetailRegistroMermaAPIView(generics.RetrieveAPIView):
    permission_classes = [LecturaTodosEscrituraSupervisor]
    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.DetailRegistroMermaSerializer


class UpdateRegistroMermaAPIView(AuditoriaSqlMixin, generics.UpdateAPIView):
    permission_classes = [LecturaTodosEscrituraSupervisor]
    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.UpdateRegistroMermaSerializer


# ======================================================
# Estaciones por linea
# ======================================================

class ListEstacionesPorLineaAPIView(APIView):
    permission_classes = [LecturaTodosEscrituraSupervisor]
    
    def get(self, request):
        linea = request.GET.get('linea')
        
        if not linea:
            return Response(
                {"error": "El parametro 'linea' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        queryset = EstacionTrabajo.objects.filter(
            linea_produccion=linea,
            activo=True,
        )

        data = EstacionTrabajoSerializer(queryset, many=True).data
        return Response(data)


class ListLotesPorComponenteAPIView(APIView):
    permission_classes = [LecturaTodosEscrituraSupervisor]

    def get(self, request):
        componente = request.GET.get('componente')

        if not componente:
            return Response(
                {"error": "El parametro 'componente' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = LoteMaterial.objects.filter(componente=componente).order_by('-fecha', '-num')
        data = serializers.LoteMaterialComboSerializer(queryset, many=True).data
        return Response(data)


class ListOrdenesPorEstacionAPIView(APIView):
    permission_classes = [LecturaTodosEscrituraSupervisor]

    def get(self, request):
        estacion = request.GET.get('estacion')

        if not estacion:
            return Response(
                {"error": "El parametro 'estacion' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = models.OrdenProduccion.objects.filter(
            estacion_trabajo=estacion,
        ).order_by('-fecha_inicio', '-numero')
        data = serializers.OrdenProduccionComboSerializer(queryset, many=True).data
        return Response(data)


# ======================================================
# Discrepancias y Recepción
# ======================================================

class ListDiscrepanciaAPIView(generics.ListAPIView):
    permission_classes = [LecturaTodosEscrituraAlmacenista]
    serializer_class = serializers.ListDiscrepanciaSerializer

    def get_queryset(self):
        queryset = models.Discrepancia.objects.all()

        # Filtramos si el Frontend envía estado=ABIERTA en la URL
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(edo_discrepancia_id=estado)

        return queryset


class DiscrepanciaCreateAPIView(AuditoriaSqlMixin, generics.CreateAPIView):
    permission_classes = [EsAlmacenista]
    queryset = models.Discrepancia.objects.all()
    serializer_class = serializers.DiscrepanciaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario_reporte=self.request.user)


class ResolverDiscrepanciaAPIView(AuditoriaSqlMixin, APIView):
    """
    RF-05/RF-48: resuelve una discrepancia y, si era la última abierta de
    su merma, reanuda el flujo a RECIBIDA en la misma operación.

    La lógica completa (validación de estado, motivo obligatorio, conteo de
    discrepancias restantes y reanudación del flujo) vive en el procedimiento
    almacenado sp_resolver_discrepancia.
    """
    permission_classes = [EsAlmacenista]

    def post(self, request, folio):
        motivo_resolucion = request.data.get('motivo_resolucion', '').strip()

        if not motivo_resolucion:
            return Response(
                {"motivo_resolucion": ["Este campo es obligatorio y no puede estar vacío."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        with connection.cursor() as cursor:
            try:
                cursor.callproc('sp_resolver_discrepancia', [
                    folio, motivo_resolucion, request.user.num,
                ])
                resultado = cursor.fetchone()
            except OperationalError as e:
                mensaje = str(e.args[1]) if len(e.args) > 1 else str(e)
                return Response({"error": mensaje}, status=status.HTTP_400_BAD_REQUEST)

        folio_merma = resultado[1]
        discrepancias_restantes = resultado[2]
        nuevo_estado_merma = 'RECIBIDA' if discrepancias_restantes == 0 else None

        return Response(
            {
                "mensaje": f"Discrepancia {folio} resuelta exitosamente.",
                "folio_discrepancia": resultado[0],
                "motivo_resolucion": motivo_resolucion,
                "merma_actualizada": folio_merma,
                "discrepancias_restantes": discrepancias_restantes,
                "nuevo_estado_merma": nuevo_estado_merma,
            },
            status=status.HTTP_200_OK
        )


class ConfirmarRecepcionAPIView(AuditoriaSqlMixin, APIView):
    """
    RF-04: confirma la recepción física del scrap en almacén.

    La lógica de validación y el cambio de estado viven en el procedimiento
    almacenado sp_confirmar_recepcion_merma (ver procedimientosAlmacenados.sql).
    El UPDATE que hace el SP dispara automáticamente tg_generar_solicitud_inspeccion,
    así que la solicitud de inspección se genera sola, sin código adicional aquí.
    """
    permission_classes = [EsAlmacenista]

    def post(self, request, folio):
        observaciones = request.data.get('observaciones', 'Sin observaciones')

        with connection.cursor() as cursor:
            try:
                cursor.callproc('sp_confirmar_recepcion_merma', [folio])
                resultado = cursor.fetchone()
            except OperationalError as e:
                # El SP usa SIGNAL SQLSTATE '45000' para sus validaciones de negocio
                # (folio inexistente, o merma que no está en REGISTRADA).
                mensaje = str(e.args[1]) if len(e.args) > 1 else str(e)
                return Response({"error": mensaje}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "mensaje": f"Recepción confirmada exitosamente para el folio {folio}.",
                "folio": resultado[0],
                "estado_actualizado": resultado[1],
                "observaciones_recibidas": observaciones,
            },
            status=status.HTTP_200_OK
        )
        
        
"""
Vista de agregación para el dashboard del rol SUPER.
Se apoya en mermas.models.RegistroMerma.
"""

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_supervisor(request):
    hoy = date.today()
    hace_6_dias = hoy - timedelta(days=6)  # ventana de 7 días incluyendo hoy

    mermas_hoy = RegistroMerma.objects.filter(fecha=hoy).count()

    semana_qs = RegistroMerma.objects.filter(fecha__gte=hace_6_dias, fecha__lte=hoy)
    mermas_semana = semana_qs.count()
    piezas_semana = semana_qs.aggregate(total=Sum('cantidad'))['total'] or 0

    # ---- Estación con más piezas mermadas en la semana ----
    estacion_top_row = (
        semana_qs.exclude(estacion_trabajo__isnull=True)
        .values('estacion_trabajo__nombre')
        .annotate(piezas=Sum('cantidad'))
        .order_by('-piezas')
        .first()
    )
    estacion_top = estacion_top_row['estacion_trabajo__nombre'] if estacion_top_row else None

    # ---- Tendencia diaria (rellenando días sin registros con 0) ----
    tendencia_qs = (
        semana_qs.values('fecha')
        .annotate(piezas=Sum('cantidad'))
        .order_by('fecha')
    )
    piezas_por_fecha = {row['fecha']: float(row['piezas'] or 0) for row in tendencia_qs}
    tendencia_semana = []
    for i in range(7):
        d = hace_6_dias + timedelta(days=i)
        tendencia_semana.append({'fecha': d.isoformat(), 'piezas': piezas_por_fecha.get(d, 0)})

    # ---- Top estaciones de la semana ----
    por_estacion_qs = (
        semana_qs.exclude(estacion_trabajo__isnull=True)
        .values('estacion_trabajo__nombre')
        .annotate(piezas=Sum('cantidad'))
        .order_by('-piezas')[:6]
    )
    por_estacion = [
        {'estacion_nombre': row['estacion_trabajo__nombre'], 'piezas': float(row['piezas'] or 0)}
        for row in por_estacion_qs
    ]

    return Response({
        'resumen': {
            'mermas_hoy': mermas_hoy,
            'mermas_semana': mermas_semana,
            'piezas_semana': float(piezas_semana),
            'estacion_top': estacion_top,
        },
        'tendencia_semana': tendencia_semana,
        'por_estacion': por_estacion,
    })
    
    """
Vista de agregación para el dashboard del rol ALMAC.
Se apoya en recepciones.models.LoteMaterial / Discrepancia y en
inspecciones.models.RegistroDisposicion (+ subtipos Devolucion/Reciclaje/Desecho).
"""
from datetime import date

from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recepciones.models import LoteMaterial, Discrepancia
from inspecciones.models import RegistroDisposicion


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_almacen(request):
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    # Lotes con stock disponible ahora mismo (no agotados, no vencidos).
    lotes_disponibles = LoteMaterial.objects.filter(estado_lote_id='DISPONIBLE').count()

    discrepancias_abiertas = Discrepancia.objects.filter(edo_discrepancia_id='ABIERTA').count()

    lotes_hoy = LoteMaterial.objects.filter(fecha=hoy).count()

    disposiciones_mes_qs = RegistroDisposicion.objects.filter(fecha_determinacion__gte=inicio_mes)
    disposiciones_mes = disposiciones_mes_qs.count()

    # ---- Disposiciones por tipo (join con los 3 subtipos vía OneToOne) ----
    devoluciones = disposiciones_mes_qs.filter(disposiciondevolucion__isnull=False).count()
    reciclaje = disposiciones_mes_qs.filter(disposicionreciclaje__isnull=False).count()
    desecho = disposiciones_mes_qs.filter(disposiciondesecho__isnull=False).count()
    disposiciones_por_tipo = [
        {'tipo': 'Devolución', 'cantidad': devoluciones},
        {'tipo': 'Reciclaje', 'cantidad': reciclaje},
        {'tipo': 'Desecho', 'cantidad': desecho},
    ]

    # ---- Discrepancias abiertas por línea ----
    # Discrepancia no tiene FK directa a línea; se llega vía
    # registro_merma -> estacion_trabajo -> linea_produccion. Como
    # registro_merma es nullable, las discrepancias sin merma asociada
    # quedan fuera de esta gráfica (se cuentan igual en el resumen).
    discrepancias_por_linea_qs = (
        Discrepancia.objects
        .filter(edo_discrepancia_id='ABIERTA')
        .exclude(registro_merma__isnull=True)
        .exclude(registro_merma__estacion_trabajo__isnull=True)
        .values('registro_merma__estacion_trabajo__linea_produccion__nombre')
        .annotate(cantidad=Count('folio'))
        .order_by('-cantidad')
    )
    discrepancias_por_linea = [
        {
            'linea_nombre': row['registro_merma__estacion_trabajo__linea_produccion__nombre'],
            'cantidad': row['cantidad'],
        }
        for row in discrepancias_por_linea_qs
    ]

    return Response({
        'resumen': {
            'lotes_disponibles': lotes_disponibles,
            'discrepancias_abiertas': discrepancias_abiertas,
            'disposiciones_mes': disposiciones_mes,
            'lotes_hoy': lotes_hoy,
        },
        'disposiciones_por_tipo': disposiciones_por_tipo,
        'discrepancias_por_linea': discrepancias_por_linea,
    })