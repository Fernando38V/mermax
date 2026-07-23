from django.db import models

# Create your models here.

"""
App: usuarios
Empleados y cuentas de usuario del sistema.

Correcciones aplicadas:
- Nombres de atributo camelCase (emNombre, emPrimerApell, emSegundoApell)
  renombrados a snake_case legible; se conserva db_column para no tocar la BD.
- on_delete=DO_NOTHING -> PROTECT (no se debe poder borrar un Área o Rol
  si hay empleados/usuarios ligados a ellos; son datos de auditoría).
- Recuerda: 'contrasena' nunca debe guardarse en texto plano. Usa
  django.contrib.auth.hashers.make_password() / check_password() al
  guardar y validar credenciales.
"""

from catalogos.models import Area, Rol


class Empleado(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre = models.CharField(db_column='emNombre', max_length=80)
    primer_apellido = models.CharField(db_column='emPrimerApell', max_length=80)
    segundo_apellido = models.CharField(db_column='emSegundoApell', max_length=80, blank=True, null=True)    
    fecha_nacimiento = models.DateField()
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