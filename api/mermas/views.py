from django.shortcuts import render, get_object_or_404

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.db import IntegrityError, DatabaseError

from mermas import serializers, models


# ======================================================
# Registro de Merma
# ======================================================

class ListRegistroMermaAPIView(APIView):

    def get(self, request):
        queryset = models.RegistroMerma.objects.all()
        data = serializers.ListRegistroMermaSerializer(
            queryset,
            many=True
        ).data
        return Response(data)


class CreateRegistroMermaAPIView(generics.CreateAPIView):
    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.CreateRegistroMermaSerializer
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class DetailRegistroMermaAPIView(generics.RetrieveAPIView):

    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.DetailRegistroMermaSerializer


class UpdateRegistroMermaAPIView(generics.UpdateAPIView):

    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.UpdateRegistroMermaSerializer


# ======================================================
# Discrepancias y Recepción
# ======================================================

class DiscrepanciaCreateAPIView(generics.CreateAPIView):
    """
    Endpoint para registrar una nueva discrepancia en el sistema.
    Usa el método POST y valida automáticamente los datos con DiscrepanciaSerializer.
    """
    queryset = models.Discrepancia.objects.all()
    serializer_class = serializers.DiscrepanciaSerializer
    
    def perform_create(self, serializer):
        serializer.save(usuario_reporte=self.request.user)


class ConfirmarRecepcionAPIView(APIView):
    def post(self, request, folio):
        # 1. Buscamos el registro en la base de datos
        registro_merma = get_object_or_404(models.RegistroMerma, folio=folio)
        
        if registro_merma.edo_flujo_merma_id != 'REGISTRADA':
            return Response(
                {
                    "error": f"No se puede confirmar la recepción. La merma se encuentra en estado '{registro_merma.edo_flujo_merma_id}' y solo se pueden recibir mermas en estado 'REGISTRADA'."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Obtenemos las observaciones que enviaste desde Postman
        observaciones = request.data.get('observaciones', 'Sin observaciones')

        # 3. ACTUALIZAMOS LA BASE DE DATOS ============================
        # Cambiamos el estado al flujo de "Recibida"
        registro_merma.edo_flujo_merma_id = 'RECIBIDA' 
        
        # Si tienes un campo en tu modelo para guardar la observación (como 'descripcion'), puedes guardarlo así:
        # registro_merma.descripcion = observaciones         
        registro_merma.save()
        # ============================================================

        return Response(
            {
                "mensaje": f"Recepción confirmada exitosamente para el folio {folio}.",
                "folio": registro_merma.folio,
                "estado_actualizado": registro_merma.edo_flujo_merma_id,
                "observaciones_recibidas": observaciones
            }, 
            status=status.HTTP_200_OK
        )