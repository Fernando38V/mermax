from rest_framework import serializers
from mermas.models import OrdenProduccion, RegistroMerma, Discrepancia
from recepciones.models import LoteMaterial


# ======================================================
# Registro de Merma
# ======================================================

class ListRegistroMermaSerializer(serializers.ModelSerializer):
    tipo_merma_nombre = serializers.CharField(source="tipo_merma.nombre", read_only=True)
    edo_merma_nombre = serializers.CharField(source="edo_flujo_merma.nombre", read_only=True)
    causa_raiz_nombre = serializers.CharField(source="causa_raiz.nombre", read_only=True)
    componente_nombre = serializers.CharField(source="componente.nombre", read_only=True)
    linea_produccion = serializers.CharField(source="estacion_trabajo.linea_produccion.num", read_only=True)
    linea_produccion_nombre = serializers.CharField(source="estacion_trabajo.linea_produccion.nombre", read_only=True)
    estacion_trabajo_nombre = serializers.CharField(source="estacion_trabajo.nombre", read_only=True) 
    class Meta:
        model = RegistroMerma
        fields = [
            "folio",
            "fecha",
            "cantidad",
            "unidad",
            "componente",
            "componente_nombre",
            "tipo_merma",
            "tipo_merma_nombre",
            "causa_raiz",
            "causa_raiz_nombre",
            "estacion_trabajo",
            "estacion_trabajo_nombre",
            "linea_produccion",
            "linea_produccion_nombre",
            "edo_flujo_merma",
            "edo_merma_nombre",
            "usuario",
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
        read_only_fields = ["usuario", "edo_flujo_merma"]

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
    
class LoteMaterialComboSerializer(serializers.ModelSerializer):
    componente_codigo = serializers.CharField(source='componente_id', read_only=True)

    class Meta:
        model = LoteMaterial
        fields = ['num', 'numero_lote_prov', 'componente', 'componente_codigo', 'fecha', 'cantidad']


class OrdenProduccionComboSerializer(serializers.ModelSerializer):
    estacion_trabajo_codigo = serializers.CharField(source='estacion_trabajo_id', read_only=True)

    class Meta:
        model = OrdenProduccion
        fields = ['numero', 'estacion_trabajo', 'estacion_trabajo_codigo', 'fecha_inicio', 'estado_orden']


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
        registro_merma = data.get('registro_merma')
        
        if registro_merma:
            estado_actual = getattr(registro_merma.edo_flujo_merma, 'pk', registro_merma.edo_flujo_merma_id)
            
            if estado_actual != 'REGISTRADA':
                raise serializers.ValidationError({
                    "registro_merma": f"No se puede crear una discrepancia para la merma '{registro_merma.folio}' porque su estado actual es '{estado_actual}'. Solo se permiten discrepancias en estado 'REGISTRADA'."
                })
        
        if cantidad_reportada is not None and cantidad_reportada < 0:
            raise serializers.ValidationError(
                {"cantidad_reportada": "La cantidad reportada no puede ser negativa."}
            )
            
        if cantidad_recibida is not None and cantidad_recibida < 0:
            raise serializers.ValidationError(
                {"cantidad_recibida": "La cantidad recibida no puede ser negativa."}
            )
            
        return data
    
class ListDiscrepanciaSerializer(serializers.ModelSerializer):
    usuario_reporte_nombre = serializers.CharField(source="usuario_reporte.username", read_only=True)
    merma_folio = serializers.CharField(source="registro_merma.folio", read_only=True)
    estado_nombre = serializers.CharField(source="edo_discrepancia.nombre", read_only=True) # Si aplica

    class Meta:
        model = Discrepancia
        fields = [
            "folio",
            "fecha_reporte",
            "cantidad_reportada",
            "cantidad_recibida",
            "diferencia",
            "motivo_reporte",
            "usuario_reporte",
            "usuario_reporte_nombre",
            "registro_merma",
            "merma_folio",
            "edo_discrepancia",
            "estado_nombre",
            "fecha_resolucion",
            "motivo_resolucion",
            "usuario_resolucion"
        ]