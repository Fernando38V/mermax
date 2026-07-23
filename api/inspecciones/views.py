from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from inspecciones import serializers, models

# Create your views here.


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