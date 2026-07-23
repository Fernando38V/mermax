from rest_framework import serializers
from inspecciones import models
from datetime import date
import re

# ======================================================
# Disposicion de devolucion a proveedor
# ======================================================

class ListDevolucionSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    
    class Meta:
        model = models.DisposicionDevolucion
        fields = [
            "folio",
            "motivo_rechazo",
            "registro_disposicion",
            "proveedor",
            "proveedor_nombre",
        ]

class CreateDevolucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisposicionDevolucion
        fields = [
            "folio",
            "motivo_rechazo",
            "registro_disposicion",
            "proveedor",
        ]
    # folio: DEV-2026-001
    def validate_folio(self, value):
        if not re.match(rf'^DEV-{date.today().year}-\d{{3}}', value):
            raise serializers.ValidationError(f'El código debe tener el formato DEV-{date.today().year}-001')
        return value

class DetailDevolucionSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    
    class Meta:
        model = models.DisposicionDevolucion
        fields = [
            "folio",
            "motivo_rechazo",
            "registro_disposicion",
            "proveedor",
            "proveedor_nombre",
        ]

class UpdateDevolucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisposicionDevolucion
        fields = [
            "motivo_rechazo",
            "registro_disposicion",
            "proveedor",
        ]
        
# ======================================================
# Disposicion de reciclaje
# ======================================================

class ListReciclajeSerializer(serializers.ModelSerializer):
    empresa_recicladora_nombre = serializers.CharField(source='empresa_recicladora.nombre', read_only=True)
    
    class Meta:
        model = models.DisposicionReciclaje
        fields = [
            "folio",
            "empresa_recicladora",
            "empresa_recicladora_nombre",
            "peso_neto",
            "registro_disposicion",
        ]

class CreateReciclajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisposicionReciclaje
        fields = [
            "folio",
            "empresa_recicladora",
            "peso_neto",
            "registro_disposicion",
        ]
    
    # folio: RCJ-2026-001
    def validate_folio(self, value):
        if not re.match(rf'^RCJ-{date.today().year}-\d{{3}}', value):
            raise serializers.ValidationError(f'El código debe tener el formato RCJ-{date.today().year}-001')
        return value
        
class DetailReciclajeSerializer(serializers.ModelSerializer):
    empresa_recicladora_nombre = serializers.CharField(source='empresa_recicladora.nombre', read_only=True)
    
    class Meta:
        model = models.DisposicionReciclaje
        fields = [
            "folio",
            "empresa_recicladora",
            "empresa_recicladora_nombre",
            "peso_neto",
            "registro_disposicion",
        ]
        
class UpdateReciclajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisposicionReciclaje
        fields = [
            "empresa_recicladora",
            "peso_neto",
            "registro_disposicion",
        ]    

# ======================================================
# Disposicion de Desecho Controlado
# ======================================================

class ListDesechoSerializer(serializers.ModelSerializer):
    metodo_destruccion_nombre = serializers.CharField(source='metodo_destruccion.nombre', read_only=True)
    
    class Meta:
        model = models.DisposicionDesecho
        fields = [
            "folio",
            "metodo_destruccion",
            "metodo_destruccion_nombre",
            "folio_probatorio",
            "registro_disposicion",
        ]
        
class CreateDesechoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisposicionDesecho
        fields = [
            "folio",
            "metodo_destruccion",
            "folio_probatorio",
            "registro_disposicion",
        ]
        
    # folio: DES-2026-001
    def validate_folio(self, value):
        if not re.match(rf'^DES-{date.today().year}-\d{{3}}', value):
            raise serializers.ValidationError(f'El código debe tener el formato DES-{date.today().year}-001')
        return value
        
class DetailDesechoSerializer(serializers.ModelSerializer):
    metodo_destruccion_nombre = serializers.CharField(source='metodo_destruccion.nombre', read_only=True)
    
    class Meta:
        model = models.DisposicionDesecho
        fields = [
            "folio",
            "metodo_destruccion",
            "metodo_destruccion_nombre",
            "folio_probatorio",
            "registro_disposicion",
        ]

class UpdateDesechoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DisposicionDesecho
        fields = [
            "metodo_destruccion",
            "folio_probatorio",
            "registro_disposicion",
        ]