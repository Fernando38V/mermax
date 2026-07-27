"""
App: usuarios - permisos por rol

RNF-02: "Cada módulo estará restringido según el rol del usuario. Un usuario
sólo puede acceder a las funciones de su rol asignado."

Todas las clases viven aquí en vez de repetirse en cada app, por dos razones:
si el reparto de roles cambia se toca un solo archivo, y para la rúbrica es
más fácil señalar un punto único donde está implementado el RNF-02.

Uso en cualquier view de DRF:

    from usuarios.permissions import EsAlmacenista

    class ConfirmarRecepcionAPIView(APIView):
        permission_classes = [EsAlmacenista]

Nota: el rol se lee con request.user.rol_id, que devuelve la clave
(SUPER / ALMAC / CALID / ADMIN) sin necesidad de una consulta extra a ROL.
"""
from rest_framework import permissions


class RolPermitido(permissions.BasePermission):
    """
    Base. Las subclases sólo declaran qué roles pasan.

    'roles_lectura' es opcional: si se define, aplica a GET/HEAD/OPTIONS y
    'roles' queda sólo para las operaciones de escritura. Sirve para los
    casos donde varios roles pueden consultar pero uno solo puede modificar.
    """
    roles = ()
    roles_lectura = None
    message = 'Tu rol no tiene permiso para esta operación.'

    def has_permission(self, request, view):
        usuario = request.user
        if not (usuario and usuario.is_authenticated):
            return False

        if request.method in permissions.SAFE_METHODS and self.roles_lectura is not None:
            permitidos = self.roles_lectura
        else:
            permitidos = self.roles

        return usuario.rol_id in permitidos


# ======================================================
# Un rol específico
# ======================================================

class EsSupervisor(RolPermitido):
    """RF-02, RF-03: registrar y corregir mermas en piso."""
    roles = ('SUPER',)
    message = 'Sólo el Supervisor de Línea puede realizar esta operación.'


class EsAlmacenista(RolPermitido):
    """RF-04, RF-05, RF-48: recibir scrap, reportar y resolver discrepancias."""
    roles = ('ALMAC',)
    message = 'Sólo el Almacenista puede realizar esta operación.'


class EsCalidad(RolPermitido):
    """RF-07 a RF-10, RF-13: inspeccionar, dictaminar y atender alertas."""
    roles = ('CALID',)
    message = 'Sólo el Ingeniero de Calidad puede realizar esta operación.'


class EsAdministrador(RolPermitido):
    """RF-15 a RF-47: catálogos, usuarios y bitácora."""
    roles = ('ADMIN',)
    message = 'Sólo el Administrador puede realizar esta operación.'


# ======================================================
# Escritura restringida, lectura abierta
# ======================================================

class LecturaTodosEscrituraSupervisor(RolPermitido):
    """
    El listado de mermas lo consultan todos los roles (el almacenista necesita
    ver qué le va a llegar, calidad qué inspeccionó), pero sólo el supervisor
    registra y corrige.
    """
    roles = ('SUPER',)
    roles_lectura = ('SUPER', 'ALMAC', 'CALID', 'ADMIN')
    message = 'Sólo el Supervisor de Línea puede registrar o modificar mermas.'


class LecturaTodosEscrituraAlmacenista(RolPermitido):
    """
    Las discrepancias las consulta cualquiera para dar seguimiento, pero sólo
    el almacenista las registra y las resuelve: son diferencias de conteo
    físico en la recepción, que es su terreno.
    """
    roles = ('ALMAC',)
    roles_lectura = ('SUPER', 'ALMAC', 'CALID', 'ADMIN')
    message = 'Sólo el Almacenista puede registrar o resolver discrepancias.'


class LecturaTodosEscrituraCalidad(RolPermitido):
    """
    Los dictámenes los consulta cualquiera (aparecen en la trazabilidad del
    RF-11), pero sólo calidad los emite.
    """
    roles = ('CALID',)
    roles_lectura = ('SUPER', 'ALMAC', 'CALID', 'ADMIN')
    message = 'Sólo el Ingeniero de Calidad puede emitir o modificar dictámenes.'


class LecturaTodosEscrituraAdmin(RolPermitido):
    """El caso de los catálogos: todos consultan, sólo el admin administra."""
    roles = ('ADMIN',)
    roles_lectura = ('SUPER', 'ALMAC', 'CALID', 'ADMIN')
    message = 'Sólo el Administrador puede modificar los catálogos.'