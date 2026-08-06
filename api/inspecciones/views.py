from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from inspecciones import serializers, models
from rest_framework import status
from django.db.models import Q, Count
from django.db import transaction
from datetime import date, datetime
from auditoria.services import AuditoriaSqlMixin

from .models import SolicitudInspeccion, RegistroDisposicion
from reportes.models import AlertaGenerada

from usuarios.permissions import EsCalidad, LecturaTodosEscrituraCalidad, EsAlmacenista

# Create your views here.

# ======================================================
# Solicitudes de Inspección View Service
# ======================================================

class ListSolicitudInspeccionAPIView(generics.ListAPIView):
    permission_classes = [EsCalidad]
    serializer_class = serializers.SolicitudInspeccionSerializer

    def get_queryset(self):
        queryset = models.SolicitudInspeccion.objects.all().order_by('-fecha_generacion', '-hora_generacion')
        
        estado = self.request.query_params.get('estado')
        q = self.request.query_params.get('q')

        if estado and estado.upper() != 'TODAS':
            queryset = queryset.filter(edo_solicitud_id=estado.upper())

        if q:
            queryset = queryset.filter(
                Q(codigo__icontains=q) | 
                Q(registro_merma__folio__icontains=q)  
            )

        return queryset

class IniciarInspeccionAPIView(AuditoriaSqlMixin, APIView):
    permission_classes = [EsCalidad]

    def post(self, request, codigo_solicitud):
        solicitud = get_object_or_404(models.SolicitudInspeccion, codigo=codigo_solicitud)

        if solicitud.edo_solicitud_id != 'PENDIENTE':
            return Response(
                {"error": "Esta solicitud ya fue atendida o no está pendiente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Traer la merma y validar que esté RECIBIDA
        registro_merma = solicitud.registro_merma
        if registro_merma.edo_flujo_merma_id != 'RECIBIDA':
            return Response(
                {"error": f"La merma actual no está RECIBIDA, su estado es {registro_merma.edo_flujo_merma_id}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Cambiar el estado de la merma a INSPECCIO
        registro_merma.edo_flujo_merma_id = 'INSPECCIO'
        registro_merma.save()

        return Response(
            {
                "mensaje": f"Inspección iniciada exitosamente para la merma {registro_merma.folio}.",
                "nuevo_estado_merma": registro_merma.edo_flujo_merma_id
            },
            status=status.HTTP_200_OK
        )


# ======================================================
# Disposicion de devolucion a proveedor View Service
# ======================================================

class ListDevolucionAPIView(generics.ListAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.ListDevolucionSerializer


class CreateDevolucionAPIView(generics.CreateAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.CreateDevolucionSerializer


class DetailDevolucionAPIView(generics.RetrieveAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.DetailDevolucionSerializer


class UpdateDevolucionAPIView(generics.UpdateAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.UpdateDevolucionSerializer


# ======================================================
# Disposicion de Reciclaje View Service
# ======================================================

class ListReciclajeAPIView(generics.ListAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.ListReciclajeSerializer


class CreateReciclajeAPIView(generics.CreateAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.CreateReciclajeSerializer


class DetailReciclajeAPIView(generics.RetrieveAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.DetailReciclajeSerializer


class UpdateReciclajeAPIView(generics.UpdateAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.UpdateReciclajeSerializer


# ======================================================
# Disposicion de Desecho Controlado View Service
# ======================================================

class ListDesechoAPIView(generics.ListAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.ListDesechoSerializer


class CreateDesechoAPIView(generics.CreateAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.CreateDesechoSerializer


class DetailDesechoAPIView(generics.RetrieveAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.DetailDesechoSerializer


class UpdateDesechoAPIView(generics.UpdateAPIView):
    permission_classes = [LecturaTodosEscrituraCalidad]
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.UpdateDesechoSerializer


# ======================================================
# Dictamen de disposición final (RF-08, RF-09, RF-10)
# ======================================================

def _siguiente_folio(modelo, prefijo, campo='folio'):
    """
    Genera el consecutivo PREFIJO-AAAA-### mirando lo que ya existe.
    Mismo criterio que usan los triggers de merma y discrepancia, para que
    toda la numeración del sistema se lea igual.
    """
    anio = date.today().year
    patron = f'{prefijo}-{anio}-'
    ultimo = 0
    for valor in modelo.objects.filter(**{f'{campo}__startswith': patron}).values_list(campo, flat=True):
        sufijo = valor[len(patron):]
        if sufijo.isdigit():
            ultimo = max(ultimo, int(sufijo))
    return f'{patron}{ultimo + 1:03d}'


class DictaminarInspeccionAPIView(AuditoriaSqlMixin, APIView):
    """
    POST /api/inspecciones/dictaminar/<codigo_solicitud>/

    Cierra el ciclo de la merma. En una sola transacción:
      1. crea el REGISTRO_DISPOSICION
      2. crea su tabla satélite según el dictamen (RF-08, RF-09 o RF-10)
      3. marca la solicitud como ATENDIDA con fecha y hora
      4. pasa la merma a CERRADA

    Los cuatro pasos van juntos o no van: si se creara la disposición y
    fallara el cierre de la merma, quedaría un folio dictaminado que la
    interfaz seguiría mostrando como pendiente de inspección.

    El registro nace con estado_disposicion = PENDIENTE. El dictamen dice qué
    hacer con el material; que ya haya salido de la planta es otra cosa, y se
    marca después con el endpoint de ejecutar.
    """
    permission_classes = [EsCalidad]

    SATELITES = {
        'RTN_PROV': ('DEV', models.DisposicionDevolucion),
        'RECICLAJE': ('RCJ', models.DisposicionReciclaje),
        'DESTR_CTRL': ('DES', models.DisposicionDesecho),
    }

    def post(self, request, codigo_solicitud):
        solicitud = get_object_or_404(models.SolicitudInspeccion, codigo=codigo_solicitud)

        if solicitud.edo_solicitud_id != 'PENDIENTE':
            return Response(
                {"error": "Esta solicitud ya fue atendida."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registro_merma = solicitud.registro_merma
        if registro_merma.edo_flujo_merma_id != 'INSPECCIO':
            return Response(
                {"error": f"La merma debe estar en INSPECCIO para dictaminarse. Su estado es {registro_merma.edo_flujo_merma_id}. Inicia la inspección primero."},
                status=status.HTTP_400_BAD_REQUEST
            )

        entrada = serializers.DictamenSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        dictamen = datos['disposicion_final']

        with transaction.atomic():
            # 1. El registro de disposición
            disposicion = models.RegistroDisposicion.objects.create(
                folio=_siguiente_folio(models.RegistroDisposicion, 'DISP'),
                fecha_determinacion=date.today(),
                fecha_ejecucion=None,
                cantidad_ejecutada=datos.get('cantidad_ejecutada') or registro_merma.cantidad,
                observaciones=datos.get('observaciones') or f'Dictamen emitido tras la inspección del folio {registro_merma.folio}.',
                sale_almacen_id='ALM-SCRP',
                llega_almacen=None,   # el material sale de la planta
                disposicion_final_id=dictamen,
                usuario=request.user,
                registro_merma=registro_merma,
                estado_disposicion_id='PENDIENTE',
            )

            # 2. La tabla satélite que corresponda
            prefijo, modelo_satelite = self.SATELITES[dictamen]
            folio_satelite = _siguiente_folio(modelo_satelite, prefijo)

            if dictamen == 'RTN_PROV':
                modelo_satelite.objects.create(
                    folio=folio_satelite,
                    motivo_rechazo=datos['motivo_rechazo'],
                    registro_disposicion=disposicion,
                    proveedor_id=datos['proveedor'],
                )
            elif dictamen == 'RECICLAJE':
                modelo_satelite.objects.create(
                    folio=folio_satelite,
                    empresa_recicladora_id=datos['empresa_recicladora'],
                    peso_neto=datos['peso_neto'],
                    registro_disposicion=disposicion,
                )
            else:
                modelo_satelite.objects.create(
                    folio=folio_satelite,
                    metodo_destruccion_id=datos['metodo_destruccion'],
                    folio_probatorio=datos['folio_probatorio'],
                    registro_disposicion=disposicion,
                )

            # 3. La solicitud queda atendida
            ahora = datetime.now()
            solicitud.edo_solicitud_id = 'ATENDIDA'
            solicitud.fecha_atencion = ahora.date()
            solicitud.hora_atencion = ahora.time().replace(microsecond=0)
            solicitud.save()

            # 4. Y la merma cierra su ciclo
            registro_merma.edo_flujo_merma_id = 'CERRADA'
            registro_merma.save()

        return Response(
            {
                "mensaje": f"Dictamen emitido para la merma {registro_merma.folio}.",
                "folio_disposicion": disposicion.folio,
                "folio_satelite": folio_satelite,
                "dictamen": dictamen,
                "solicitud": solicitud.codigo,
                "nuevo_estado_merma": registro_merma.edo_flujo_merma_id,
            },
            status=status.HTTP_201_CREATED
        )


class ListRegistroDisposicionAPIView(generics.ListAPIView):
    """
    GET /api/inspecciones/disposicion/list/?estado=PENDIENTE&dictamen=RECICLAJE
    """
    permission_classes = [LecturaTodosEscrituraCalidad]
    serializer_class = serializers.RegistroDisposicionSerializer

    def get_queryset(self):
        qs = (models.RegistroDisposicion.objects
              .select_related('disposicion_final', 'estado_disposicion', 'usuario')
              .order_by('-fecha_determinacion', '-folio'))

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado_disposicion_id=estado.upper())

        dictamen = self.request.query_params.get('dictamen')
        if dictamen:
            qs = qs.filter(disposicion_final_id=dictamen.upper())

        return qs


class EjecutarDisposicionAPIView(AuditoriaSqlMixin, APIView):
    """
    POST /api/inspecciones/disposicion/ejecutar/<folio>/

    Marca que el material ya salió físicamente de la planta: se devolvió al
    proveedor, se entregó a la recicladora o se destruyó. Es lo que separa
    "ya se decidió qué hacer" de "ya se hizo".
    """
    permission_classes = [EsAlmacenista]

    def post(self, request, folio):
        disposicion = get_object_or_404(models.RegistroDisposicion, folio=folio)

        if disposicion.estado_disposicion_id == 'EJECUTADO':
            return Response(
                {"error": "Esta disposición ya fue ejecutada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        disposicion.estado_disposicion_id = 'EJECUTADO'
        disposicion.fecha_ejecucion = date.today()
        disposicion.save()

        return Response(
            {
                "mensaje": f"Disposición {folio} marcada como ejecutada.",
                "fecha_ejecucion": disposicion.fecha_ejecucion,
            },
            status=status.HTTP_200_OK
        )

# ======================================================
# Dashboard de calidad
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_calidad(request):
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
 
    # ---- Resumen ----
    inspecciones_pendientes = SolicitudInspeccion.objects.filter(
        edo_solicitud_id='PENDIENTE'
    ).count()
 
    atendidas_hoy = SolicitudInspeccion.objects.filter(
        fecha_atencion=hoy
    ).count()
 
    alertas_activas = AlertaGenerada.objects.filter(
        estado_alerta_id='ACTIVA'
    ).count()
 
    disposiciones_mes = RegistroDisposicion.objects.filter(
        fecha_determinacion__gte=inicio_mes
    )
    total_disposiciones = disposiciones_mes.count()
    devoluciones = disposiciones_mes.filter(
        disposiciondevolucion__isnull=False
    ).count()
    pct_devolucion = round((devoluciones / total_disposiciones) * 100, 1) if total_disposiciones else 0
 
    # ---- Inspecciones por estado (para la dona) ----
    inspecciones_por_estado_qs = (
        SolicitudInspeccion.objects
        .values('edo_solicitud__nombre')
        .annotate(cantidad=Count('codigo'))
        .order_by('edo_solicitud__nombre')
    )
    inspecciones_por_estado = [
        {'estado': item['edo_solicitud__nombre'], 'cantidad': item['cantidad']}
        for item in inspecciones_por_estado_qs
    ]
 
    # ---- Alertas activas por línea (para la barra) ----
    alertas_por_linea_qs = (
        AlertaGenerada.objects
        .filter(estado_alerta_id='ACTIVA')
        .values('umbral_alerta__linea_produccion__nombre')
        .annotate(cantidad=Count('num'))
        .order_by('-cantidad')
    )
    alertas_por_linea = [
        {'linea_nombre': item['umbral_alerta__linea_produccion__nombre'], 'cantidad': item['cantidad']}
        for item in alertas_por_linea_qs
    ]
 
    return Response({
        'resumen': {
            'inspecciones_pendientes': inspecciones_pendientes,
            'alertas_activas': alertas_activas,
            'atendidas_hoy': atendidas_hoy,
            'pct_devolucion': pct_devolucion,
        },
        'inspecciones_por_estado': inspecciones_por_estado,
        'alertas_por_linea': alertas_por_linea,
    })