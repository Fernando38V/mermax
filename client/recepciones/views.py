from datetime import date, datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction

from mermas.models import RegistroMerma
from catalogos.models import EdoFlujoMerma, EdoDiscrepancia, EdoSolicitud
from inspecciones.models import SolicitudInspeccion
from recepciones.models import Discrepancia
from recepciones.serializers import (
    DiscrepanciaCreateSerializer,
    ResolucionDiscrepanciaSerializer,
    ConfirmarRecepcionSerializer,
)

# Códigos de catálogo usados en este módulo — evita strings mágicos repetidos
EDO_FLUJO_REGISTRADA = 'REGISTRADA'
EDO_FLUJO_RECIBIDA = 'RECIBIDA'
EDO_FLUJO_DISCREPANCIA = 'DISCREPAN'
EDO_SOLICITUD_PENDIENTE = 'PENDIENTE'
EDO_DISCREPANCIA_ABIERTA = 'ABIERTA'
EDO_DISCREPANCIA_RESUELTA = 'RESUELTA'


class RecepcionesPendientesListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        mermas = RegistroMerma.objects.filter(edo_flujo_merma_id=EDO_FLUJO_REGISTRADA)
        data = []
        for m in mermas:
            data.append({
                'folio': m.folio,  # folio ES el identificador — no hay id numérico separado
                'fecha': m.fecha,
                'cantidad': m.cantidad,
                'unidad': m.unidad,
                'componente': m.componente.nombre if m.componente else None,
                'estacion': m.estacion_trabajo.nombre if m.estacion_trabajo else None,
                'edo_flujo_merma': m.edo_flujo_merma_id,
                'usuario': m.usuario.username,
            })
        return Response(data, status=status.HTTP_200_OK)


class ConfirmarRecepcionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = ConfirmarRecepcionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        folio = serializer.validated_data['folio_merma']
        try:
            merma = RegistroMerma.objects.get(folio=folio)
        except RegistroMerma.DoesNotExist:
            return Response({'error': 'Merma no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            edo_recibido = EdoFlujoMerma.objects.get(codigo=EDO_FLUJO_RECIBIDA)
            edo_sol_pendiente = EdoSolicitud.objects.get(codigo=EDO_SOLICITUD_PENDIENTE)
        except (EdoFlujoMerma.DoesNotExist, EdoSolicitud.DoesNotExist) as e:
            return Response({'error': f'Catálogo no configurado: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        merma.edo_flujo_merma = edo_recibido
        merma.save()

        ahora = datetime.now()
        SolicitudInspeccion.objects.create(
            codigo=f"SOL-{merma.folio}",
            fecha_generacion=ahora.date(),
            hora_generacion=ahora.time(),
            edo_solicitud=edo_sol_pendiente,
            registro_merma=merma,
            usuario=request.user,
        )
        return Response({'detail': 'Recepción confirmada.'}, status=status.HTTP_200_OK)


class DiscrepanciaCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        registro_merma_folio = request.data.get('registro_merma')
        merma = None
        if registro_merma_folio:
            try:
                merma = RegistroMerma.objects.get(folio=registro_merma_folio)
            except RegistroMerma.DoesNotExist:
                return Response({'error': 'Merma no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['usuario_reporte'] = request.user.num
        serializer = DiscrepanciaCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Folio y fecha de la discrepancia se generan aquí, no los manda el cliente
        folio_discrepancia = f"DISC-{merma.folio if merma else registro_merma_folio}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        discrepancia = serializer.save(
            folio=folio_discrepancia,
            fecha_reporte=date.today(),
        )

        if merma:
            try:
                edo_disc = EdoFlujoMerma.objects.get(codigo=EDO_FLUJO_DISCREPANCIA)
            except EdoFlujoMerma.DoesNotExist:
                return Response({'error': f'Catálogo edo_flujo_merma "{EDO_FLUJO_DISCREPANCIA}" no configurado.'},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            merma.edo_flujo_merma = edo_disc
            merma.save()

        return Response(
            {
                'folio': discrepancia.folio,
                'cantidad_reportada': discrepancia.cantidad_reportada,
                'cantidad_recibida': discrepancia.cantidad_recibida,
                'diferencia': discrepancia.diferencia,
                'motivo_reporte': discrepancia.motivo_reporte,
            },
            status=status.HTTP_201_CREATED,
        )


class ResolverDiscrepanciaAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, folio_discrepancia):
        serializer = ResolucionDiscrepanciaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            discrepancia = Discrepancia.objects.get(folio=folio_discrepancia)
        except Discrepancia.DoesNotExist:
            return Response({'error': 'Discrepancia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            edo_resuelta = EdoDiscrepancia.objects.get(codigo=EDO_DISCREPANCIA_RESUELTA)
        except EdoDiscrepancia.DoesNotExist:
            return Response({'error': f'Catálogo edo_discrepancia "{EDO_DISCREPANCIA_RESUELTA}" no configurado.'},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        discrepancia.edo_discrepancia = edo_resuelta
        discrepancia.motivo_resolucion = serializer.validated_data['motivo_resolucion']
        discrepancia.fecha_resolucion = date.today()
        discrepancia.usuario_resolucion = request.user
        discrepancia.save()

        merma = discrepancia.registro_merma
        if merma and not Discrepancia.objects.filter(
            registro_merma=merma, edo_discrepancia_id=EDO_DISCREPANCIA_ABIERTA
        ).exists():
            try:
                edo_recibida = EdoFlujoMerma.objects.get(codigo=EDO_FLUJO_RECIBIDA)
                edo_sol = EdoSolicitud.objects.get(codigo=EDO_SOLICITUD_PENDIENTE)
            except (EdoFlujoMerma.DoesNotExist, EdoSolicitud.DoesNotExist) as e:
                return Response({'error': f'Catálogo no configurado: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            merma.edo_flujo_merma = edo_recibida
            merma.save()
            ahora = datetime.now()
            SolicitudInspeccion.objects.get_or_create(
                codigo=f"SOL-{merma.folio}",
                defaults={
                    'fecha_generacion': ahora.date(),
                    'hora_generacion': ahora.time(),
                    'edo_solicitud': edo_sol,
                    'registro_merma': merma,
                    'usuario': request.user,
                },
            )

        return Response({'detail': 'Discrepancia resuelta.'}, status=status.HTTP_200_OK)