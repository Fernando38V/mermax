from rest_framework import serializers
from catalogos import models
import re

# ======================================================
# Empresas Recicladoras
# ======================================================

class ListRecicladoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmpresaRecicladora
        fields = [
            "nombre",
            "telefono",
            "correo",
            "activo",
        ]

class CreateRecicladoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmpresaRecicladora
        fields = [
            "codigo",
            "nombre",
            "telefono",
            "correo",
            "activo",
        ]
    
    def validate_codigo(self, value):
        if not re.match(r'^REC-\d{2}$', value):
            raise serializers.ValidationError("El código debe tener el formato REC-01")
        return value
    
class DetailRecicladoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmpresaRecicladora
        fields = [
            "codigo",
            "nombre",
            "telefono",
            "correo",
            "activo",
        ]        

class UpdateRecicladoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmpresaRecicladora
        fields = [
            "codigo",
            "nombre",
            "telefono",
            "correo",
            "activo",
        ]
        
# ======================================================
# Metodos de destruccion
# ======================================================

class ListMetodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetodoDestruccion
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "activo",
        ]

class CreateMetodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetodoDestruccion
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "activo",
        ]
    
    def validate_codigo(self, value):
        if not re.match(r'^MET-\d{2}$', value):
            raise serializers.ValidationError("El código debe tener el formato MET-01")
        return value
    
class DetailMetodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetodoDestruccion
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "activo",
        ]        

class UpdateMetodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MetodoDestruccion
        fields = [
            "nombre",
            "descripcion",
            "activo",
        ]

