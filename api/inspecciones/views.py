from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from inspecciones import serializers, models
from rest_framework import status

# Create your views here.

# ======================================================
# Solicitudes de Inspección View Service
# ======================================================

class ListSolicitudInspeccionAPIView(generics.ListAPIView):
    serializer_class = serializers.SolicitudInspeccionSerializer

    def get_queryset(self):
        return models.SolicitudInspeccion.objects.filter(edo_solicitud_id='PENDIENTE')

class IniciarInspeccionAPIView(APIView):
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
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.ListDevolucionSerializer
    
class CreateDevolucionAPIView(generics.CreateAPIView):
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.CreateDevolucionSerializer
    
class DetailDevolucionAPIView(generics.RetrieveAPIView):
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.DetailDevolucionSerializer
    
class UpdateDevolucionAPIView(generics.UpdateAPIView):
    queryset = models.DisposicionDevolucion.objects.all()
    serializer_class = serializers.UpdateDevolucionSerializer
    
# ======================================================
# Disposicion de Reciclaje View Service
# ======================================================

class ListReciclajeAPIView(generics.ListAPIView):
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.ListReciclajeSerializer
    
class CreateReciclajeAPIView(generics.CreateAPIView):
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.CreateReciclajeSerializer

class DetailReciclajeAPIView(generics.RetrieveAPIView):
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.DetailReciclajeSerializer
    
class UpdateReciclajeAPIView(generics.UpdateAPIView):
    queryset = models.DisposicionReciclaje.objects.all()
    serializer_class = serializers.UpdateReciclajeSerializer
        
# ======================================================
# Disposicion de Desecho Controlado View Service
# ======================================================

class ListDesechoAPIView(generics.ListAPIView):
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.ListDesechoSerializer
    
class CreateDesechoAPIView(generics.CreateAPIView):
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.CreateDesechoSerializer
    
class DetailDesechoAPIView(generics.RetrieveAPIView):
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.DetailDesechoSerializer
    
class UpdateDesechoAPIView(generics.UpdateAPIView):
    queryset = models.DisposicionDesecho.objects.all()
    serializer_class = serializers.UpdateDesechoSerializer