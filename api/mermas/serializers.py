from rest_framework import serializers
from mermas.models import RegistroMerma, Discrepancia


# ======================================================
# Registro de Merma
# ======================================================

class ListRegistroMermaSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegistroMerma
        fields = [
            "folio",
            "fecha",
            "cantidad",
            "unidad",
            "tipo_merma",
            "usuario",
            "edo_flujo_merma",
        ]


class CreateRegistroMermaSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegistroMerma
        fields = [
            "cantidad",
            "unidad",
            "descripcion",
            "edo_flujo_merma",
            "usuario",
            "lote_material",
            "componente",
            "tipo_merma",
            "causa_raiz",
            "estacion_trabajo",
            "orden_produccion",
        ]
        read_only_fields = ["usuario"]

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad debe ser mayor que cero."
            )
        return value

class DetailRegistroMermaSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegistroMerma
        fields = "__all__"


class UpdateRegistroMermaSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegistroMerma
        fields = [
            "cantidad",
            "unidad",
            "descripcion",
            "edo_flujo_merma",
            "lote_material",
            "componente",
            "tipo_merma",
            "causa_raiz",
            "estacion_trabajo",
            "orden_produccion",
        ]

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "La cantidad debe ser mayor que cero."
            )
        return value
    
# ======================================================
# Discrepancias
# ======================================================

class DiscrepanciaSerializer(serializers.ModelSerializer):
    folio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Discrepancia
        fields = "__all__"
        read_only_fields = ["folio", "diferencia", "fecha_reporte", "usuario_reporte"]

    def validate(self, data):
        cantidad_reportada = data.get('cantidad_reportada')
        cantidad_recibida = data.get('cantidad_recibida')
        
        if cantidad_reportada is not None and cantidad_reportada < 0:
            raise serializers.ValidationError(
                {"cantidad_reportada": "La cantidad reportada no puede ser negativa."}
            )
            
        if cantidad_recibida is not None and cantidad_recibida < 0:
            raise serializers.ValidationError(
                {"cantidad_recibida": "La cantidad recibida no puede ser negativa."}
            )
            
        return data