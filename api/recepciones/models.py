from django.db import models

# Create your models here.

"""
App: recepciones
Lotes de material que entran a planta y discrepancias detectadas al recibirlos.

Correcciones aplicadas:
- on_delete=DO_NOTHING -> PROTECT para catálogos (componente, almacén,
  estado_lote, proveedor) y para 'usuario' (registro de auditoría).
- 'registro_merma' en Discrepancia es opcional en el SQL (nullable), por lo
  que se usa SET_NULL: si se borra el registro de merma relacionado, la
  discrepancia no debe desaparecer, solo perder la referencia.
- Referencias a modelos de otras apps se hacen con string 'app.Modelo' para
  evitar imports circulares (mermas también referencia a este módulo).
"""

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