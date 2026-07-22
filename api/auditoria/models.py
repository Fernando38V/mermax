from django.db import models

# Create your models here.

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