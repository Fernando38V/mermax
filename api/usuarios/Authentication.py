"""
Autenticación por token estilo rest_framework.authtoken, pero usando
nuestro propio modelo Token (ver models.py) apuntado a Usuario en vez
de a AUTH_USER_MODEL.

El cliente manda el header:
    Authorization: Token <key>

CORREGIDO 25/07: ya existe el campo 'activo' en la tabla usuario, así que
se activa la validación que estaba comentada. RF-46 pide que al desactivar
una cuenta se revoque el acceso de inmediato: sin esta comprobación, un
usuario dado de baja seguiría entrando con el token que ya tenía.
"""
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .models import Token


class UsuarioTokenAuthentication(TokenAuthentication):
    keyword = 'Token'
    model = Token

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.select_related(
                'usuario', 'usuario__rol', 'usuario__empleado'
            ).get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido')

        # RF-46: revocación inmediata de acceso al desactivar la cuenta
        if not token.usuario.activo:
            token.delete()
            raise exceptions.AuthenticationFailed('Usuario inactivo')

        return (token.usuario, token)