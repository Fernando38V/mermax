from rest_framework import serializers
from recepciones.models import Discrepancia


class DiscrepanciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discrepancia
        # folio y fecha_reporte se generan server-side en la view, no los expone el cliente
        fields = [
            'cantidad_reportada', 'cantidad_recibida',
            'diferencia', 'motivo_reporte', 'registro_merma', 'usuario_reporte',
        ]


class ResolucionDiscrepanciaSerializer(serializers.Serializer):
    motivo_resolucion = serializers.CharField(max_length=100, required=True)


class ConfirmarRecepcionSerializer(serializers.Serializer):
    folio_merma = serializers.CharField(max_length=20, required=True)