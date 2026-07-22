from django.db import models

# Create your models here.

"""
App: inspecciones
Solicitudes de inspección de calidad (RF-05/RF-06, trigger
trg_generar_solicitud_inspeccion) y el registro de disposición final.

Correcciones aplicadas:
- on_delete=DO_NOTHING -> PROTECT en catálogos, usuario y registro_merma
  NOT NULL de RegistroDisposicion (es un registro de auditoría: no debe
  poder perderse el rastro de qué merma se dispuso).
- SET_NULL en 'registro_merma' de SolicitudInspeccion (nullable en el SQL)
  y en las dos FK a Almacen de RegistroDisposicion (también nullable).
- related_name explícitos en 'sale_almacen' / 'llega_almacen' para
  reemplazar el feo 'registrodisposicion_llega_almacen_set' que generó
  inspectdb por choque de nombres (dos FK al mismo modelo Almacen).
"""

from catalogos.models import Almacen, DisposicionFinal, EdoSolicitud, EmpresaRecicladora, EstadoDisposicion, MetodoDestruccion, Proveedor
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
