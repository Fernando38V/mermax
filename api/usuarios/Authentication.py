"""
Autenticación por token estilo rest_framework.authtoken, pero usando
nuestro propio modelo Token (ver models.py) apuntado a Usuario en vez
de a AUTH_USER_MODEL.

El cliente manda el header:
    Authorization: Token <key>
"""
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .models import Token


class UsuarioTokenAuthentication(TokenAuthentication):
    keyword = 'Token'
    model = Token

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.select_related('usuario', 'usuario__rol', 'usuario__empleado').get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido')

        # Si más adelante agregas un campo 'activo' a Usuario, valida aquí:
        # if not token.usuario.activo:
        #     raise exceptions.AuthenticationFailed('Usuario inactivo')

        return (token.usuario, token)