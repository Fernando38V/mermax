"""
App: catalogos - serializers

Cubre dos cosas distintas:

1. CATÁLOGOS ADMINISTRABLES (CRUD completo). Son los que los RF piden que el
   Administrador pueda dar de alta, editar, consultar y dar de baja:
       Líneas de producción     RF-15 a RF-18
       Componentes o piezas     RF-19 a RF-22
       Proveedores              RF-23 a RF-26
       Estaciones de trabajo    RF-27 a RF-30
       Causas raíz              RF-35 a RF-38
       Tipos de merma           RF-39 a RF-42

2. CATÁLOGOS DE SÓLO LECTURA. Estados, turnos, roles, KPIs, plantas, áreas,
   almacenes y productos. No hay RF que pida administrarlos desde la interfaz:
   existen para llenar los combos de los formularios. Exponerlos como
   editables sería darle al Administrador la posibilidad de romper el flujo
   (por ejemplo borrando el estado 'RECIBIDA', del que dependen los triggers).

Nota sobre la baja lógica: ningún catálogo se borra físicamente. Los RF-18,
22, 26, 30, 38 y 42 piden conservar el histórico, así que la baja cambia
'activo' a False (o 'estado_linea' a INACTIVA en el caso de las líneas).
"""
from rest_framework import serializers

from .models import (
    Almacen, Area, CausaRaiz, Componente, DisposicionFinal, EdoFlujoMerma,
    EdoSolicitud, EmpresaRecicladora, EstacionTrabajo, EstadoAlerta,
    EstadoDisposicion, EstadoLinea, EstadoLote, EstadoOrden, IndicadorKpi,
    LineaProduccion, MetodoDestruccion, Planta, Producto, Proveedor, Rol,
    TipoMerma, Turno,
)


# ======================================================
# Catálogos de sólo lectura (para poblar combos)
# ======================================================

class CatalogoSimpleSerializer(serializers.ModelSerializer):
    """Para los catálogos de código + nombre, que son casi todos."""
    class Meta:
        fields = ('codigo', 'nombre')


class EstadoLineaSerializer(CatalogoSimpleSerializer):
    class Meta(CatalogoSimpleSerializer.Meta):
        model = EstadoLinea


class EstadoOrdenSerializer(CatalogoSimpleSerializer):
    class Meta(CatalogoSimpleSerializer.Meta):
        model = EstadoOrden


class EstadoLoteSerializer(CatalogoSimpleSerializer):
    class Meta(CatalogoSimpleSerializer.Meta):
        model = EstadoLote


class EstadoAlertaSerializer(CatalogoSimpleSerializer):
    class Meta(CatalogoSimpleSerializer.Meta):
        model = EstadoAlerta


class EstadoDisposicionSerializer(CatalogoSimpleSerializer):
    class Meta(CatalogoSimpleSerializer.Meta):
        model = EstadoDisposicion


class EdoFlujoMermaSerializer(CatalogoSimpleSerializer):
    class Meta(CatalogoSimpleSerializer.Meta):
        model = EdoFlujoMerma


class EdoSolicitudSerializer(CatalogoSimpleSerializer):
    class Meta(CatalogoSimpleSerializer.Meta):
        model = EdoSolicitud


class DisposicionFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisposicionFinal
        fields = ('clave', 'nombre', 'descripcion')


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ('clave', 'nombre', 'descripcion')


class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = ('clave', 'nombre', 'hora_inicio', 'hora_fin')


class IndicadorKpiSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorKpi
        fields = ('codigo', 'nombre', 'descripcion', 'formula', 'unidad')


class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planta
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    planta_nombre = serializers.CharField(source='planta.nombre', read_only=True)

    class Meta:
        model = Area
        fields = ('codigo', 'nombre', 'descripcion', 'planta', 'planta_nombre')


class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class EmpresaRecicladoraSerializer(serializers.ModelSerializer):
    """Catálogo de apoyo del dictamen de reciclaje (RF-09)."""
    class Meta:
        model = EmpresaRecicladora
        fields = ('codigo', 'nombre', 'telefono', 'correo', 'activo')


class MetodoDestruccionSerializer(serializers.ModelSerializer):
    """Catálogo de apoyo del dictamen de desecho controlado (RF-10)."""
    class Meta:
        model = MetodoDestruccion
        fields = ('codigo', 'nombre', 'descripcion', 'activo')


# ======================================================
# RF-15 a RF-18: Líneas de producción
# ======================================================

class LineaProduccionSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado_linea.nombre', read_only=True)

    class Meta:
        model = LineaProduccion
        fields = ('num', 'nombre', 'descripcion', 'numero_linea',
                  'area', 'area_nombre', 'estado_linea', 'estado_nombre')

    def validate_numero_linea(self, value):
        """RF-15 exige identificador único de línea."""
        qs = LineaProduccion.objects.filter(numero_linea=value)
        if self.instance:
            qs = qs.exclude(num=self.instance.num)
        if qs.exists():
            raise serializers.ValidationError('Ya existe una línea con ese número.')
        return value


# ======================================================
# RF-19 a RF-22: Componentes o piezas
# ======================================================

class ComponenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Componente
        fields = ('codigo', 'nombre', 'costo', 'descripcion', 'tipo', 'activo')

    def validate_costo(self, value):
        """
        El costo unitario alimenta directamente el cálculo del Trigger 1
        (costo_total = cantidad x costo). Un costo negativo o nulo produce
        KPIs financieros sin sentido.
        """
        if value is None or value <= 0:
            raise serializers.ValidationError('El costo unitario debe ser mayor a cero.')
        return value


# ======================================================
# RF-23 a RF-26: Proveedores
# ======================================================

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ('codigo', 'nombre', 'correo', 'telefono',
                  'direccion_calle', 'direccion_numero', 'direccion_colonia',
                  'rfc', 'activo')
        extra_kwargs = {
            # RF-23: el correo de contacto es obligatorio al dar de alta
            'correo': {'required': True, 'allow_null': False, 'allow_blank': False},
        }


# ======================================================
# RF-27 a RF-30: Estaciones de trabajo
# ======================================================

class EstacionTrabajoSerializer(serializers.ModelSerializer):
    linea_nombre = serializers.CharField(source='linea_produccion.nombre', read_only=True)

    class Meta:
        model = EstacionTrabajo
        fields = ('codigo', 'nombre', 'etapa',
                  'linea_produccion', 'linea_nombre', 'activo')


# ======================================================
# RF-35 a RF-38: Causas raíz
# ======================================================

class CausaRaizSerializer(serializers.ModelSerializer):
    class Meta:
        model = CausaRaiz
        fields = ('codigo', 'nombre', 'descripcion', 'activo')


# ======================================================
# RF-39 a RF-42: Tipos de merma
# ======================================================

class TipoMermaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMerma
        fields = ('codigo', 'nombre', 'descripcion', 'activo')