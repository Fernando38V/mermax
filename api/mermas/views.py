from django.shortcuts import render, get_object_or_404

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.db import IntegrityError, DatabaseError, transaction
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

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
        
class CreateRegistroMermaAPIView(generics.CreateAPIView):
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


class UpdateRegistroMermaAPIView(generics.UpdateAPIView):
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


class DiscrepanciaCreateAPIView(generics.CreateAPIView):
    permission_classes = [EsAlmacenista]
    queryset = models.Discrepancia.objects.all()
    serializer_class = serializers.DiscrepanciaSerializer

    def perform_create(self, serializer):
        serializer.save(usuario_reporte=self.request.user)


class ResolverDiscrepanciaAPIView(APIView):
    permission_classes = [EsAlmacenista]

    def post(self, request, folio):
        discrepancia = get_object_or_404(models.Discrepancia, folio=folio)

        if discrepancia.edo_discrepancia_id == 'RESUELTA':
            return Response(
                {"error": "Esta discrepancia ya se encuentra cerrada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        motivo_resolucion = request.data.get('motivo_resolucion', '').strip()

        if not motivo_resolucion:
            return Response(
                {"motivo_resolucion": ["Este campo es obligatorio y no puede estar vacío."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Los dos cambios van juntos o no van. Si el segundo fallara por su
        # cuenta, la discrepancia quedaría resuelta pero la merma seguiría
        # bloqueada y sin solicitud: un estado del que no se puede salir
        # desde la interfaz.
        with transaction.atomic():
            discrepancia.edo_discrepancia_id = 'RESUELTA'
            discrepancia.usuario_resolucion = request.user  # El almacenista del 2do turno
            discrepancia.motivo_resolucion = motivo_resolucion
            discrepancia.fecha_resolucion = timezone.now().date()
            discrepancia.save()

            # Como ya se aclaró la diferencia, la merma pasa a 'RECIBIDA'.
            # Este save dispara el Trigger 2, que genera la solicitud de
            # inspección al no encontrar ya discrepancias abiertas.
            # El orden importa: primero la discrepancia, después la merma.
            registro_merma = discrepancia.registro_merma
            registro_merma.edo_flujo_merma_id = 'RECIBIDA'
            registro_merma.save()

        return Response(
            {
                "mensaje": f"Discrepancia {folio} resuelta exitosamente.",
                "folio_discrepancia": discrepancia.folio,
                "motivo_resolucion": discrepancia.motivo_resolucion,
                "merma_actualizada": registro_merma.folio,
                "nuevo_estado_merma": registro_merma.edo_flujo_merma_id
            },
            status=status.HTTP_200_OK
        )


class ConfirmarRecepcionAPIView(APIView):
    permission_classes = [EsAlmacenista]

    def post(self, request, folio):
        registro_merma = get_object_or_404(models.RegistroMerma, folio=folio)

        if registro_merma.edo_flujo_merma_id != 'REGISTRADA':
            return Response(
                {
                    "error": f"No se puede confirmar la recepción. La merma se encuentra en estado '{registro_merma.edo_flujo_merma_id}' y solo se pueden recibir mermas en estado 'REGISTRADA'."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        observaciones = request.data.get('observaciones', 'Sin observaciones')

        # 3.Cambiamos el estado al flujo de "Recibida"
        registro_merma.edo_flujo_merma_id = 'RECIBIDA'

        registro_merma.save()

        return Response(
            {
                "mensaje": f"Recepción confirmada exitosamente para el folio {folio}.",
                "folio": registro_merma.folio,
                "estado_actualizado": registro_merma.edo_flujo_merma_id,
                "observaciones_recibidas": observaciones
            },
            status=status.HTTP_200_OK
        )