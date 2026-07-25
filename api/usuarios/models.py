"""
App: usuarios
Empleados y cuentas de usuario del sistema.

Correcciones aplicadas:
- Nombres de atributo camelCase (emNombre, emPrimerApell, emSegundoApell)
  renombrados a snake_case legible; se conserva db_column para no tocar la BD.
- on_delete=DO_NOTHING -> PROTECT (no se debe poder borrar un Área o Rol
  si hay empleados/usuarios ligados a ellos; son datos de auditoría).
- CORREGIDO 25/07: se quitó 'fecha_nacimiento'. Esa columna NO existe en la
  tabla 'empleado'; con managed=False Django la mandaba en el SELECT y
  tronaba con "Unknown column 'fecha_nacimiento'" (error 1054) en cualquier
  consulta que tocara Empleado, incluido el login (select_related).
- CORREGIDO 25/07: se quitó 'puesto' (se duplicaba con Usuario.rol, acuerdo
  de equipo) y se agregó 'turno' (RF-31 pide turno asignado al empleado).
- Recuerda: 'contrasena' nunca debe guardarse en texto plano. Usa
  django.contrib.auth.hashers.make_password() / check_password() al
  guardar y validar credenciales.
"""
from django.db import models

from catalogos.models import Area, Rol, Turno


class Empleado(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre = models.CharField(db_column='emNombre', max_length=80)
    primer_apellido = models.CharField(db_column='emPrimerApell', max_length=80)
    segundo_apellido = models.CharField(db_column='emSegundoApell', max_length=80, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, db_column='area')
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT, db_column='turno', blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'empleado'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.nombre} {self.primer_apellido}'

    @property
    def nombre_completo(self):
        partes = [self.nombre, self.primer_apellido, self.segundo_apellido]
        return ' '.join(p for p in partes if p)


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

    # DRF y el decorador de permisos preguntan por esto cuando el objeto
    # hace las veces de request.user. Sin ellos, IsAuthenticated rechaza
    # al usuario aunque el token sea válido.
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


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
    y administrar (managed=True, el default), así que cada vez que
    reimportes mermax.sql tienes que volver a correr:
        python manage.py migrate
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