"""
App: home (cliente) - context processors

El sidebar de layout_app.html necesita saber el rol del usuario en TODAS
las páginas, no sólo en el dashboard. En vez de que cada vista tenga que
acordarse de mandar 'usuario' en el contexto, este context processor lo
inyecta automáticamente desde la sesión.

Para activarlo, en client/settings.py agrega la última línea:

    TEMPLATES = [{
        ...
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.usuario_sesion',
            ],
        },
    }]
"""


def usuario_sesion(request):
    """
    Deja disponible en las plantillas:
      usuario.num, usuario.username, usuario.correo,
      usuario.rol          -> clave del rol: SUPER / ALMAC / CALID / ADMIN
      usuario.rol_nombre   -> nombre legible del rol
      usuario.nombre_completo
    """
    return {'usuario': request.session.get('usuario')}