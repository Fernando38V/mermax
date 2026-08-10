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
from django.db import connection
from django.db.utils import OperationalError
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

    RF-08/RF-09/RF-10: cierra el ciclo de la merma en dos pasos, cada uno
    en su propio procedimiento almacenado (responsabilidad única):

      sp_generar_registro_disposicion  -> crea el REGISTRO_DISPOSICION y su
                                           tabla satélite según el dictamen
      sp_cerrar_solicitud_inspeccion   -> marca la solicitud ATENDIDA y
                                           cierra la merma a CERRADA

    Ambos se llaman en secuencia desde aquí; si el primero falla, el
    segundo nunca se ejecuta.
    """
    permission_classes = [EsCalidad]

    def post(self, request, codigo_solicitud):
        solicitud = get_object_or_404(models.SolicitudInspeccion, codigo=codigo_solicitud)
        folio_merma = solicitud.registro_merma_id

        entrada = serializers.DictamenSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        dictamen = datos['disposicion_final']

        with connection.cursor() as cursor:
            try:
                # sp_generar_registro_disposicion tiene un parámetro OUT
                # (folioDisposicion) al final; MySQLdb lo resuelve solo
                # cuando se le manda None como valor inicial.
                parametros = [
                    folio_merma,
                    dictamen,
                    request.user.num,
                    datos.get('cantidad_ejecutada'),
                    datos.get('observaciones'),
                    datos.get('proveedor'),
                    datos.get('motivo_rechazo'),
                    datos.get('empresa_recicladora'),
                    datos.get('peso_neto'),
                    datos.get('metodo_destruccion'),
                    datos.get('folio_probatorio'),
                    None,  # OUT folioDisposicion
                ]
                resultado_sp3 = cursor.callproc('sp_generar_registro_disposicion', parametros)
                folio_disposicion = resultado_sp3[-1]

                cursor.callproc('sp_cerrar_solicitud_inspeccion', [
                    codigo_solicitud, folio_merma, request.user.num,
                ])
                resultado_sp4 = cursor.fetchone()

            except OperationalError as e:
                mensaje = str(e.args[1]) if len(e.args) > 1 else str(e)
                return Response({"error": mensaje}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "mensaje": f"Dictamen emitido para la merma {folio_merma}.",
                "folio_disposicion": folio_disposicion,
                "dictamen": dictamen,
                "solicitud": resultado_sp4[0],
                "nuevo_estado_merma": resultado_sp4[2],
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

    Marca que el material ya salió físicamente de la planta. La validación
    de que la merma asociada esté CERRADA (regla que antes no se verificaba
    en el backend) vive ahora en sp_ejecutar_disposicion_final.
    """
    permission_classes = [EsAlmacenista]

    def post(self, request, folio):
        with connection.cursor() as cursor:
            try:
                cursor.callproc('sp_ejecutar_disposicion_final', [folio])
                resultado = cursor.fetchone()
            except OperationalError as e:
                mensaje = str(e.args[1]) if len(e.args) > 1 else str(e)
                return Response({"error": mensaje}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "mensaje": f"Disposición {folio} marcada como ejecutada.",
                "fecha_ejecucion": resultado[2],
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