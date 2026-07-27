"""
App: reportes - serializers

Cubre RF-11 (trazabilidad de lote), RF-12 (dashboard de KPIs),
RF-13 (alertas automáticas) y RF-14 (reportes exportables).

Los KPIs no tienen un modelo detrás: se calculan con agregaciones sobre
REGISTRO_MERMA y TURNO_ORDEN. Por eso la mayoría son Serializers planos
y no ModelSerializers.
"""
from rest_framework import serializers

from .models import AlertaGenerada, UmbralAlerta


# ======================================================
# RF-13: Umbrales y alertas
# ======================================================

class UmbralAlertaSerializer(serializers.ModelSerializer):
    linea_nombre = serializers.CharField(source='linea_produccion.nombre', read_only=True)
    kpi_nombre = serializers.CharField(source='indicador_kpi.nombre', read_only=True)
    unidad = serializers.CharField(source='indicador_kpi.unidad', read_only=True)

    class Meta:
        model = UmbralAlerta
        fields = ('numero', 'valor', 'activo', 'indicador_kpi', 'kpi_nombre',
                  'unidad', 'linea_produccion', 'linea_nombre')


class AlertaGeneradaSerializer(serializers.ModelSerializer):
    linea_nombre = serializers.CharField(
        source='umbral_alerta.linea_produccion.nombre', read_only=True)
    kpi_nombre = serializers.CharField(
        source='umbral_alerta.indicador_kpi.nombre', read_only=True)
    valor_umbral = serializers.DecimalField(
        source='umbral_alerta.valor', max_digits=10, decimal_places=2, read_only=True)
    unidad = serializers.CharField(
        source='umbral_alerta.indicador_kpi.unidad', read_only=True)
    estado_nombre = serializers.CharField(source='estado_alerta.nombre', read_only=True)
    atendida_por = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = AlertaGenerada
        fields = ('num', 'fecha', 'valor_detectado', 'valor_umbral', 'unidad',
                  'observaciones', 'estado_alerta', 'estado_nombre',
                  'umbral_alerta', 'linea_nombre', 'kpi_nombre', 'atendida_por')


class AtenderAlertaSerializer(serializers.Serializer):
    """
    RF-13: la alerta bloquea su estado hasta ser atendida y cerrada con una
    observación. Por eso el texto es obligatorio y no puede ir vacío.
    """
    observaciones = serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True)

    def validate_observaciones(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                'Describe brevemente la acción tomada (mínimo 10 caracteres).'
            )
        return value.strip()


# ======================================================
# RF-12: Dashboard
# ======================================================

class LineaKpiSerializer(serializers.Serializer):
    """Una fila del semáforo por línea de producción."""
    linea = serializers.IntegerField()
    linea_nombre = serializers.CharField()
    piezas_producidas = serializers.IntegerField()
    piezas_mermadas = serializers.FloatField()
    porcentaje_scrap = serializers.FloatField()
    costo_scrap = serializers.DecimalField(max_digits=14, decimal_places=2)
    umbral = serializers.FloatField(allow_null=True)
    semaforo = serializers.CharField()   # verde / amarillo / rojo / sin_umbral


class CausaRaizKpiSerializer(serializers.Serializer):
    """Una fila del ranking de causas raíz."""
    causa_raiz = serializers.CharField()
    nombre = serializers.CharField()
    eventos = serializers.IntegerField()
    piezas = serializers.FloatField()
    costo = serializers.DecimalField(max_digits=14, decimal_places=2)


# ======================================================
# RF-11: Trazabilidad de lote
# ======================================================

class TrazabilidadLoteSerializer(serializers.Serializer):
    lote = serializers.IntegerField()
    numero_lote_proveedor = serializers.CharField(allow_null=True)
    componente = serializers.CharField()
    componente_nombre = serializers.CharField()
    proveedor = serializers.CharField()
    fecha_recepcion = serializers.DateField()
    cantidad_recibida = serializers.FloatField()
    cantidad_mermada = serializers.FloatField()
    cantidad_aprovechada = serializers.FloatField()
    porcentaje_merma = serializers.FloatField()
    costo_desperdicio = serializers.DecimalField(max_digits=14, decimal_places=2)


# ======================================================
# RF-14: Reporte detallado
# ======================================================

class MermaReporteSerializer(serializers.Serializer):
    folio = serializers.CharField()
    fecha = serializers.DateField()
    linea = serializers.CharField()
    estacion = serializers.CharField()
    turno = serializers.CharField(allow_null=True)
    componente = serializers.CharField()
    cantidad = serializers.FloatField()
    costo_total = serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=True)
    tipo_merma = serializers.CharField(allow_null=True)
    causa_raiz = serializers.CharField(allow_null=True)
    estado = serializers.CharField()
    dictamen = serializers.CharField(allow_null=True)