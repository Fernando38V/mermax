from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from catalogos import serializers, models

# Create your views here.

# Empresa Recicladora View Service

class ListRecicladoraAPIView(APIView):
    
    def get(self, request):
        queryset = models.EmpresaRecicladora.objects.all()
        data = serializers.ListRecicladoraSerializer(queryset, many=True).data
        return Response(data)

class CreateRecicladoraAPIView(generics.CreateAPIView):
    queryset = models.EmpresaRecicladora.objects.all()
    serializer_class = serializers.CreateRecicladoraSerializer
    
class DetailRecicladoraAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.EmpresaRecicladora.objects.all()
    serializer_class = serializers.DetailRecicladoraSerializer
    
class UpdateRecicladoraAPIView(generics.UpdateAPIView):
    queryset = models.EmpresaRecicladora.objects.all()
    serializer_class = serializers.UpdateRecicladoraSerializer