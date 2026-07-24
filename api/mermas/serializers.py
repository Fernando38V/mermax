from rest_framework import serializers
from mermas.models import RegistroMerma


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