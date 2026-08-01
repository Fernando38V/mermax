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
            raise serializers.ValidationError(f'El código debe tener el formato DEV-{date.today().year}-001')
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
            raise serializers.ValidationError(f'El código debe tener el formato RCJ-{date.today().year}-001')
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
            raise serializers.ValidationError(f'El código debe tener el formato DES-{date.today().year}-001')
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

# ======================================================
# Solicitudes de Inspección
# ======================================================

class SolicitudInspeccionSerializer(serializers.ModelSerializer):
    estado_merma = serializers.CharField(source='registro_merma.edo_flujo_merma_id', read_only=True)
    class Meta:
        model = models.SolicitudInspeccion
        fields = '__all__'


# ======================================================
# Dictamen de disposición final (RF-08, RF-09, RF-10)
# ======================================================

class DictamenSerializer(serializers.Serializer):
    """
    Valida la entrada del dictamen. No es un ModelSerializer porque una sola
    petición produce dos filas: el REGISTRO_DISPOSICION y su tabla satélite.

    Cada dictamen exige campos distintos, y los RF los marcan obligatorios:
        RTN_PROV    proveedor + motivo_rechazo            (RF-08)
        RECICLAJE   empresa_recicladora + peso_neto       (RF-09)
        DESTR_CTRL  metodo_destruccion + folio_probatorio (RF-10)
    """
    disposicion_final = serializers.ChoiceField(
        choices=['RTN_PROV', 'RECICLAJE', 'DESTR_CTRL']
    )
    cantidad_ejecutada = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    observaciones = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    # RF-08: devolución a proveedor
    proveedor = serializers.CharField(max_length=10, required=False)
    motivo_rechazo = serializers.CharField(max_length=255, required=False)

    # RF-09: reciclaje
    empresa_recicladora = serializers.CharField(max_length=10, required=False)
    peso_neto = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    # RF-10: desecho controlado
    metodo_destruccion = serializers.CharField(max_length=10, required=False)
    folio_probatorio = serializers.CharField(max_length=10, required=False)

    REQUERIDOS = {
        'RTN_PROV': ('proveedor', 'motivo_rechazo'),
        'RECICLAJE': ('empresa_recicladora', 'peso_neto'),
        'DESTR_CTRL': ('metodo_destruccion', 'folio_probatorio'),
    }

    def validate(self, data):
        dictamen = data['disposicion_final']
        faltantes = [
            campo for campo in self.REQUERIDOS[dictamen]
            if data.get(campo) in (None, '')
        ]
        if faltantes:
            raise serializers.ValidationError({
                campo: f'Obligatorio para el dictamen {dictamen}.'
                for campo in faltantes
            })

        if data.get('peso_neto') is not None and data['peso_neto'] <= 0:
            raise serializers.ValidationError(
                {'peso_neto': 'El peso neto debe ser mayor a cero.'}
            )
        return data


class RegistroDisposicionSerializer(serializers.ModelSerializer):
    dictamen_nombre = serializers.CharField(source='disposicion_final.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado_disposicion.nombre', read_only=True)
    emitido_por = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = models.RegistroDisposicion
        fields = [
            'folio',
            'fecha_determinacion',
            'fecha_ejecucion',
            'cantidad_ejecutada',
            'observaciones',
            'sale_almacen',
            'llega_almacen',
            'disposicion_final',
            'dictamen_nombre',
            'estado_disposicion',
            'estado_nombre',
            'usuario',
            'emitido_por',
            'registro_merma',
        ]