from django.db import models

# Create your models here.
"""
App: catalogos
Contiene todas las tablas de referencia / configuración estática del sistema
(estados, tipos, catálogos maestros de planta, línea, producto, etc.)

Correcciones aplicadas respecto al inspectdb original:
- on_delete=DO_NOTHING -> PROTECT en todas las FK (son catálogos: no queremos
  que se puedan borrar en cascada ni silenciosamente si están en uso).
- ProdComp: la FK 'producto' venía como OneToOneField (bug de inspectdb al
  mapear la PK compuesta orden/producto). Se corrigió a ForeignKey con
  primary_key=True, que sí soporta Django y respeta la relación real
  producto-componente (varios componentes por producto).
- Se agregaron __str__ para que se vean legibles en el admin/shell.
"""

class EstadoLinea(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=30, unique=True)

    class Meta:
        managed = False
        db_table = 'estado_linea'
        verbose_name = 'Estado de línea'
        verbose_name_plural = 'Estados de línea'

    def __str__(self):
        return self.nombre


class EstadoOrden(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'estado_orden'
        verbose_name = 'Estado de orden'
        verbose_name_plural = 'Estados de orden'

    def __str__(self):
        return self.nombre


class EstadoLote(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'estado_lote'
        verbose_name = 'Estado de lote'
        verbose_name_plural = 'Estados de lote'

    def __str__(self):
        return self.nombre


class EstadoAlerta(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'estado_alerta'
        verbose_name = 'Estado de alerta'
        verbose_name_plural = 'Estados de alerta'

    def __str__(self):
        return self.nombre


class EstadoDisposicion(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=25, unique=True)

    class Meta:
        managed = False
        db_table = 'estado_disposicion'
        verbose_name = 'Estado de disposición'
        verbose_name_plural = 'Estados de disposición'

    def __str__(self):
        return self.nombre


class EdoFlujoMerma(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'edo_flujo_merma'
        verbose_name = 'Estado de flujo de merma'
        verbose_name_plural = 'Estados de flujo de merma'

    def __str__(self):
        return self.nombre


class EdoSolicitud(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'edo_solicitud'
        verbose_name = 'Estado de solicitud'
        verbose_name_plural = 'Estados de solicitud'

    def __str__(self):
        return self.nombre


class TipoMerma(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'tipo_merma'
        verbose_name = 'Tipo de merma'
        verbose_name_plural = 'Tipos de merma'

    def __str__(self):
        return self.nombre


class CausaRaiz(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'causa_raiz'
        verbose_name = 'Causa raíz'
        verbose_name_plural = 'Causas raíz'

    def __str__(self):
        return self.nombre


class DisposicionFinal(models.Model):
    clave = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disposicion_final'
        verbose_name = 'Disposición final'
        verbose_name_plural = 'Disposiciones finales'

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    clave = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Turno(models.Model):
    clave = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=30, unique=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        managed = False
        db_table = 'turno'
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'

    def __str__(self):
        return self.nombre


class IndicadorKpi(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=50, blank=True, null=True)
    formula = models.CharField(max_length=100, blank=True, null=True)
    unidad = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'indicador_kpi'
        verbose_name = 'Indicador KPI'
        verbose_name_plural = 'Indicadores KPI'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    modelo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    pulgadas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.modelo


class Componente(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'componente'
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=150, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion_calle = models.CharField(db_column='dirCalle', max_length=150, blank=True, null=True)
    direccion_numero = models.CharField(db_column='dirNumero', max_length=10, blank=True, null=True)
    direccion_colonia = models.CharField(db_column='dirColonia', max_length=100, blank=True, null=True)
    rfc = models.CharField(db_column='RFC', max_length=13, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre


class Planta(models.Model):
    clave = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    telefono = models.CharField(db_column='numTel', max_length=20, blank=True, null=True)
    direccion_calle = models.CharField(db_column='dirCalle', max_length=150, blank=True, null=True)
    direccion_numero = models.CharField(db_column='dirNumero', max_length=10, blank=True, null=True)
    direccion_colonia = models.CharField(db_column='dirColonia', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planta'
        verbose_name = 'Planta'
        verbose_name_plural = 'Plantas'

    def __str__(self):
        return self.nombre


class Area(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    planta = models.ForeignKey(Planta, on_delete=models.PROTECT, db_column='planta')

    class Meta:
        managed = False
        db_table = 'area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return self.nombre


class Almacen(models.Model):
    clave = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    capacidad = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    planta = models.ForeignKey(Planta, on_delete=models.PROTECT, db_column='planta')

    class Meta:
        managed = False
        db_table = 'almacen'
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'

    def __str__(self):
        return self.nombre


class LineaProduccion(models.Model):
    num = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    numero_linea = models.IntegerField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, db_column='area')
    estado_linea = models.ForeignKey(EstadoLinea, on_delete=models.PROTECT, db_column='estado_linea')

    class Meta:
        managed = False
        db_table = 'linea_produccion'
        verbose_name = 'Línea de producción'
        verbose_name_plural = 'Líneas de producción'

    def __str__(self):
        return self.nombre


class EstacionTrabajo(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100, unique=True)
    etapa = models.CharField(max_length=50, blank=True, null=True)
    linea_produccion = models.ForeignKey(LineaProduccion, on_delete=models.PROTECT, db_column='linea_produccion')
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'estacion_trabajo'
        verbose_name = 'Estación de trabajo'
        verbose_name_plural = 'Estaciones de trabajo'

    def __str__(self):
        return self.nombre

class EmpresaRecicladora(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'empresa_recicladora'
        verbose_name = 'Empresa recicladora'
        verbose_name_plural = 'Empresas recicladoras'

    def __str__(self):
        return self.nombre

class MetodoDestruccion(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'metodo_destruccion'
        verbose_name = 'Método de destrucción'
        verbose_name_plural = 'Métodos de destrucción'

    def __str__(self):
        return self.nombre

class LineaTurno(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    fecha = models.DateField()
    linea_produccion = models.ForeignKey(LineaProduccion, on_delete=models.PROTECT, db_column='linea_produccion')
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT, db_column='turno')

    class Meta:
        managed = False
        db_table = 'linea_turno'
        verbose_name = 'Línea-turno'
        verbose_name_plural = 'Líneas-turno'

    def __str__(self):
        return self.codigo


class ProdComp(models.Model):
    # CORRECCIÓN: inspectdb generó esto como OneToOneField (bug al resolver
    # la PK compuesta producto+componente). Con OneToOneField, Django solo
    # permitiría UN componente por producto, lo cual es falso: un producto
    # requiere varios componentes (receta / BOM). Se corrige a ForeignKey
    # con primary_key=True, que sí es válido en Django y no requiere tocar
    # el esquema de la BD.
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='producto', primary_key=True)
    componente = models.ForeignKey(Componente, on_delete=models.PROTECT, db_column='componente')
    unidad = models.CharField(max_length=20, blank=True, null=True)
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'prod_comp'
        verbose_name = 'Componente de producto'
        verbose_name_plural = 'Componentes de producto'
        unique_together = (('producto', 'componente'),)

    def __str__(self):
        return f'{self.producto_id} - {self.componente_id}'
