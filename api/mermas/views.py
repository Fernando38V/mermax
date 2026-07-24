from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
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


class DetailRegistroMermaAPIView(generics.RetrieveAPIView):

    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.DetailRegistroMermaSerializer


class UpdateRegistroMermaAPIView(generics.UpdateAPIView):

    queryset = models.RegistroMerma.objects.all()
    serializer_class = serializers.UpdateRegistroMermaSerializer