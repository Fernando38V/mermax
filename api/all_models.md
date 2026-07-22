MODELS DEL PROYECTO

## Models de catalogos

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

## Models de usuarios

from catalogos.models import Area, Rol


class Empleado(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre = models.CharField(db_column='emNombre', max_length=80)
    primer_apellido = models.CharField(db_column='emPrimerApell', max_length=80)
    segundo_apellido = models.CharField(db_column='emSegundoApell', max_length=80, blank=True, null=True)
    puesto = models.CharField(max_length=80, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, db_column='area')
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'empleado'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.nombre} {self.primer_apellido}'


class Usuario(models.Model):
    num = models.AutoField(primary_key=True)
    contrasena = models.CharField(max_length=255)
    username = models.CharField(max_length=50)
    correo = models.CharField(max_length=50)
    empleado = models.OneToOneField(Empleado, on_delete=models.PROTECT, db_column='empleado')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column='rol')
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username


def _generar_token_key():
    import binascii
    import os
    return binascii.hexlify(os.urandom(20)).decode()
  
class Token(models.Model):
    """
    Equivalente al Token de rest_framework.authtoken, pero apuntando a
    nuestro modelo Usuario en vez de a AUTH_USER_MODEL.
 
    OJO: a diferencia de los demás modelos de este archivo, esta tabla
    NO existe en mermax.sql. Es una tabla nueva que Django sí debe crear
    y administrar (managed=True, el default), así que después de agregar
    esta clase corre:
        python manage.py makemigrations usuarios
        python manage.py migrate usuarios
    """
    key = models.CharField(max_length=40, primary_key=True)
    usuario = models.OneToOneField(Usuario, related_name='auth_token', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'usuario_token'
        verbose_name = 'Token de acceso'
        verbose_name_plural = 'Tokens de acceso'
 
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = _generar_token_key()
        return super().save(*args, **kwargs)
 
    def __str__(self):
        return self.key

## Models de mermas

from catalogos.models import (
    CausaRaiz, Componente, EdoFlujoMerma, EstacionTrabajo, EstadoOrden,
    Producto, TipoMerma, Turno,
)
from usuarios.models import Usuario


class OrdenProduccion(models.Model):
    numero = models.AutoField(primary_key=True)
    cantidad_inicial = models.IntegerField()
    cantidad_final = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estacion_trabajo = models.ForeignKey(EstacionTrabajo, on_delete=models.PROTECT, db_column='estacion_trabajo')
    estado_orden = models.ForeignKey(EstadoOrden, on_delete=models.PROTECT, db_column='estado_orden')

    class Meta:
        managed = False
        db_table = 'orden_produccion'
        verbose_name = 'Orden de producción'
        verbose_name_plural = 'Órdenes de producción'

    def __str__(self):
        return f'Orden {self.numero}'


class OrdenProducto(models.Model):
    orden = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE, db_column='orden', primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column='producto')
    cantidad = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'orden_producto'
        verbose_name = 'Producto de orden'
        verbose_name_plural = 'Productos de orden'
        unique_together = (('orden', 'producto'),)

    def __str__(self):
        return f'{self.orden_id} - {self.producto_id}'


class TurnoOrden(models.Model):
    clave = models.CharField(primary_key=True, max_length=10)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    cantidad_producida = models.IntegerField(blank=True, null=True)
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT, db_column='turno')
    orden_produccion = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE, db_column='orden_produccion')

    class Meta:
        managed = False
        db_table = 'turno_orden'
        verbose_name = 'Turno de orden'
        verbose_name_plural = 'Turnos de orden'

    def __str__(self):
        return self.clave


class RegistroMerma(models.Model):
    folio = models.CharField(primary_key=True, max_length=20)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha = models.DateField()
    unidad = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    edo_flujo_merma = models.ForeignKey(EdoFlujoMerma, on_delete=models.PROTECT, db_column='edo_flujo_merma')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='usuario')
    lote_material = models.ForeignKey(
        'recepciones.LoteMaterial', on_delete=models.SET_NULL,
        db_column='lote_material', blank=True, null=True
    )
    componente = models.ForeignKey(
        Componente, on_delete=models.SET_NULL,
        db_column='componente', blank=True, null=True
    )
    tipo_merma = models.ForeignKey(TipoMerma, on_delete=models.PROTECT, db_column='tipo_merma')
    causa_raiz = models.ForeignKey(
        CausaRaiz, on_delete=models.SET_NULL,
        db_column='causa_raiz', blank=True, null=True
    )
    estacion_trabajo = models.ForeignKey(
        EstacionTrabajo, on_delete=models.SET_NULL,
        db_column='estacion_trabajo', blank=True, null=True
    )
    orden_produccion = models.ForeignKey(
        OrdenProduccion, on_delete=models.SET_NULL,
        db_column='orden_produccion', blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'registro_merma'
        verbose_name = 'Registro de merma'
        verbose_name_plural = 'Registros de merma'

    def __str__(self):
        return self.folio

## Models de recepciones

from catalogos.models import Almacen, Componente, EstadoLote, Proveedor
from usuarios.models import Usuario


class LoteMaterial(models.Model):
    num = models.AutoField(primary_key=True)
    fecha = models.DateField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    caducidad = models.DateField(blank=True, null=True)
    numero_lote_prov = models.CharField(max_length=50, blank=True, null=True)
    componente = models.ForeignKey(Componente, on_delete=models.PROTECT, db_column='componente')
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, db_column='almacen')
    estado_lote = models.ForeignKey(EstadoLote, on_delete=models.PROTECT, db_column='estado_lote')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, db_column='proveedor')

    class Meta:
        managed = False
        db_table = 'lote_material'
        verbose_name = 'Lote de material'
        verbose_name_plural = 'Lotes de material'

    def __str__(self):
        return f'Lote {self.num} - {self.componente_id}'


class Discrepancia(models.Model):
    folio = models.CharField(primary_key=True, max_length=20)
    fecha = models.DateField()
    cantidad_reportada = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_recibida = models.DecimalField(max_digits=10, decimal_places=2)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='usuario')
    registro_merma = models.ForeignKey(
        'mermas.RegistroMerma', on_delete=models.SET_NULL,
        db_column='registro_merma', blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'discrepancia'
        verbose_name = 'Discrepancia'
        verbose_name_plural = 'Discrepancias'

    def __str__(self):
        return self.folio

## Models de inspecciones

from catalogos.models import (
    Almacen, DisposicionFinal, EdoSolicitud, EmpresaRecicladora,
    EstadoDisposicion, MetodoDestruccion, Proveedor,
)
from usuarios.models import Usuario


class SolicitudInspeccion(models.Model):
    codigo = models.CharField(primary_key=True, max_length=20)
    fecha_generacion = models.DateField()
    hora_generacion = models.TimeField()
    fecha_atencion = models.DateField(blank=True, null=True)
    hora_atencion = models.TimeField(blank=True, null=True)
    edo_solicitud = models.ForeignKey(EdoSolicitud, on_delete=models.PROTECT, db_column='edo_solicitud')
    registro_merma = models.ForeignKey(
        'mermas.RegistroMerma', on_delete=models.SET_NULL,
        db_column='registro_merma', blank=True, null=True
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='usuario')

    class Meta:
        managed = False
        db_table = 'solicitud_inspeccion'
        verbose_name = 'Solicitud de inspección'
        verbose_name_plural = 'Solicitudes de inspección'

    def __str__(self):
        return self.codigo


class RegistroDisposicion(models.Model):
    folio = models.CharField(primary_key=True, max_length=20)
    fecha_determinacion = models.DateField()
    fecha_ejecucion = models.DateField(blank=True, null=True)
    cantidad_ejecutada = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    sale_almacen = models.ForeignKey(
        Almacen, on_delete=models.SET_NULL, db_column='sale_almacen',
        related_name='disposiciones_salida', blank=True, null=True
    )
    llega_almacen = models.ForeignKey(
        Almacen, on_delete=models.SET_NULL, db_column='llega_almacen',
        related_name='disposiciones_entrada', blank=True, null=True
    )
    disposicion_final = models.ForeignKey(DisposicionFinal, on_delete=models.PROTECT, db_column='disposicion_final')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='usuario')
    registro_merma = models.ForeignKey(
        'mermas.RegistroMerma', on_delete=models.PROTECT, db_column='registro_merma'
    )
    estado_disposicion = models.ForeignKey(EstadoDisposicion, on_delete=models.PROTECT, db_column='estado_disposicion')

    class Meta:
        managed = False
        db_table = 'registro_disposicion'
        verbose_name = 'Registro de disposición'
        verbose_name_plural = 'Registros de disposición'

    def __str__(self):
        return self.folio


class DisposicionDevolucion(models.Model):
    """RF-08: Devolución a proveedor."""
    folio = models.CharField(primary_key=True, max_length=20)
    motivo_rechazo = models.CharField(max_length=255)
    registro_disposicion = models.OneToOneField(
        RegistroDisposicion, on_delete=models.CASCADE, db_column='registro_disposicion'
    )
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, db_column='proveedor')

    class Meta:
        managed = False
        db_table = 'disposicion_devolucion'
        verbose_name = 'Devolución a proveedor'
        verbose_name_plural = 'Devoluciones a proveedor'

    def __str__(self):
        return self.folio


class DisposicionReciclaje(models.Model):
    """RF-09: Reciclaje."""
    folio = models.CharField(primary_key=True, max_length=20)
    empresa_recicladora = models.ForeignKey(
        EmpresaRecicladora, on_delete=models.PROTECT, db_column='empresa_recicladora'
    )
    peso_neto = models.DecimalField(max_digits=10, decimal_places=2)
    registro_disposicion = models.OneToOneField(
        RegistroDisposicion, on_delete=models.CASCADE, db_column='registro_disposicion'
    )

    class Meta:
        managed = False
        db_table = 'disposicion_reciclaje'
        verbose_name = 'Disposición de reciclaje'
        verbose_name_plural = 'Disposiciones de reciclaje'

    def __str__(self):
        return self.folio


class DisposicionDesecho(models.Model):
    """RF-10: Desecho controlado."""
    folio = models.CharField(primary_key=True, max_length=20)
    metodo_destruccion = models.ForeignKey(
        MetodoDestruccion, on_delete=models.PROTECT, db_column='metodo_destruccion'
    )
    folio_probatorio = models.CharField(max_length=10)
    registro_disposicion = models.OneToOneField(
        RegistroDisposicion, on_delete=models.CASCADE, db_column='registro_disposicion'
    )

    class Meta:
        managed = False
        db_table = 'disposicion_desecho'
        verbose_name = 'Disposición de desecho controlado'
        verbose_name_plural = 'Disposiciones de desecho controlado'

    def __str__(self):
        return self.folio

## Models de reportes

from catalogos.models import EstadoAlerta, IndicadorKpi, LineaProduccion
from usuarios.models import Usuario


class UmbralAlerta(models.Model):
    numero = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField()
    indicador_kpi = models.ForeignKey(IndicadorKpi, on_delete=models.PROTECT, db_column='indicador_kpi')
    linea_produccion = models.ForeignKey(LineaProduccion, on_delete=models.PROTECT, db_column='linea_produccion')

    class Meta:
        managed = False
        db_table = 'umbral_alerta'
        verbose_name = 'Umbral de alerta'
        verbose_name_plural = 'Umbrales de alerta'

    def __str__(self):
        return f'Umbral {self.numero} - {self.indicador_kpi_id}'


class AlertaGenerada(models.Model):
    num = models.AutoField(primary_key=True)
    fecha = models.DateField()
    observaciones = models.CharField(max_length=100, blank=True, null=True)
    valor_detectado = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column='usuario', blank=True, null=True
    )
    estado_alerta = models.ForeignKey(EstadoAlerta, on_delete=models.PROTECT, db_column='estado_alerta')
    umbral_alerta = models.ForeignKey(UmbralAlerta, on_delete=models.PROTECT, db_column='umbral_alerta')

    class Meta:
        managed = False
        db_table = 'alerta_generada'
        verbose_name = 'Alerta generada'
        verbose_name_plural = 'Alertas generadas'

    def __str__(self):
        return f'Alerta {self.num}'

## Models de auditoria

from usuarios.models import Usuario


class BitacoraAuditoria(models.Model):
    num = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='usuario')
    modulo = models.CharField(max_length=50)
    accion = models.CharField(max_length=20)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'bitacora_auditoria'
        verbose_name = 'Bitácora de auditoría'
        verbose_name_plural = 'Bitácoras de auditoría'

    def __str__(self):
        return f'Bitácora {self.num} - {self.modulo}'