"""
App: auditoria
RF-47 - Bitácora de auditoría del sistema.

La tabla BITACORA_AUDITORIA existe físicamente en mermax.sql pero, por
decisión del equipo, NO se representa en el DER ni en el MR: se documenta
como funcionalidad transversal, no como entidad del modelo de negocio.

El RF-47 dice que la bitácora "será únicamente de consulta y no podrá ser
modificada ni eliminada". Eso no se cumple solo con no exponer los endpoints:
aquí se bloquea a nivel de modelo, para que ni siquiera un error de
programación pueda alterar un registro ya escrito.
"""
from django.db import models

from usuarios.models import Usuario


class BitacoraNoModificable(Exception):
    """Se lanza al intentar alterar o borrar un registro ya escrito."""
    pass


class BitacoraAuditoria(models.Model):
    ACCIONES = [
        ('CREATE', 'Alta'),
        ('UPDATE', 'Modificación'),
        ('DELETE', 'Baja'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
    ]

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
        verbose_name = 'Registro de bitácora'
        verbose_name_plural = 'Bitácora de auditoría'
        ordering = ['-fecha_hora', '-num']

    def __str__(self):
        return f'{self.fecha_hora:%Y-%m-%d %H:%M} · {self.modulo} · {self.accion}'

    # --- RF-47: inmutabilidad ------------------------------------------

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise BitacoraNoModificable(
                'Un registro de bitácora no puede modificarse (RF-47).'
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise BitacoraNoModificable(
            'Un registro de bitácora no puede eliminarse (RF-47).'
        )