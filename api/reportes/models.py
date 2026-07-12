from django.db import models

# Create your models here.

"""
App: reportes
Umbrales de alerta por KPI/línea y las alertas generadas cuando se rebasan.

Correcciones aplicadas:
- 'activo' en UmbralAlerta corregido de IntegerField a BooleanField (el SQL
  lo define como BOOLEAN NOT NULL; inspectdb lo mapeó mal porque MySQL
  guarda BOOLEAN como TINYINT(1)).
- on_delete=DO_NOTHING -> PROTECT para catálogos y umbral_alerta.
- 'usuario' en AlertaGenerada es nullable en el SQL -> SET_NULL.
"""

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