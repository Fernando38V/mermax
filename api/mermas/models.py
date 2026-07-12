from django.db import models

# Create your models here.

"""
App: mermas
Núcleo del sistema: órdenes de producción, turnos de orden y el registro
de merma en sí.

Correcciones aplicadas:
- OrdenProducto: igual que ProdComp en catalogos, inspectdb generó
  OneToOneField sobre 'orden' por la PK compuesta (orden, producto), lo cual
  impediría que una orden tenga más de un producto. Se corrige a ForeignKey
  con primary_key=True.
- on_delete=DO_NOTHING reemplazado por:
    * PROTECT en catálogos y en 'usuario' (auditoría).
    * SET_NULL en las FK opcionales de RegistroMerma (lote_material,
      componente, causa_raiz, estacion_trabajo, orden_produccion), tal
      como ya estaban definidas como nullable en el SQL.
    * CASCADE en OrdenProducto/TurnoOrden -> OrdenProduccion, porque esos
      registros no tienen sentido sin la orden a la que pertenecen.
"""

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