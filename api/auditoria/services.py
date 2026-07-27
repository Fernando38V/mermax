"""
App: auditoria - servicios

El RF-47 pide que la bitácora se llene "de forma automática". Aquí están las
dos piezas para lograrlo sin repetir código en cada view:

    registrar(...)     una llamada suelta, para casos puntuales (login, etc.)
    BitacoraMixin      se agrega a cualquier view de DRF y registra solo
                       las altas, ediciones y bajas de ese recurso

Sobre el uso de super() en el mixin: los tres métodos delegan la operación
real a la clase de abajo en lugar de hacerla ellos. Eso importa porque el
CatalogoAdminViewSet convierte el DELETE en baja lógica; si el mixin llamara
a instance.delete() por su cuenta, borraría físicamente el registro y se
saltaría esa regla. Así, el mixin sólo observa y anota.

Limitación que conviene tener clara: esto registra lo que pasa por el ORM a
través de las vistas. Las operaciones hechas con QuerySet.update(), con SQL
directo o por los triggers NO pasan por aquí. Para esas, la auditoría vive en
la propia base (los triggers y las restricciones), no en esta bitácora.
"""
import json

from django.forms.models import model_to_dict

from .models import BitacoraAuditoria

# Campos que nunca deben quedar escritos en la bitácora aunque el modelo
# los tenga: son credenciales.
CAMPOS_SENSIBLES = {'contrasena', 'password', 'token', 'key'}


def _serializar(instancia):
    """Convierte una instancia a JSON legible, sin campos sensibles."""
    if instancia is None:
        return None
    try:
        datos = model_to_dict(instancia)
    except Exception:
        return str(instancia)

    limpio = {}
    for campo, valor in datos.items():
        if campo in CAMPOS_SENSIBLES:
            limpio[campo] = '***'
        else:
            limpio[campo] = str(valor) if valor is not None else None
    return json.dumps(limpio, ensure_ascii=False)


def registrar(usuario, modulo, accion, anterior=None, nuevo=None, motivo=None):
    """
    Escribe una línea en la bitácora. Nunca lanza excepción hacia arriba:
    si la auditoría falla, no debe tumbar la operación que la originó.
    """
    if usuario is None or not getattr(usuario, 'num', None):
        return None
    try:
        return BitacoraAuditoria.objects.create(
            usuario=usuario,
            modulo=modulo[:50],
            accion=accion[:20],
            valor_anterior=anterior if isinstance(anterior, str) else _serializar(anterior),
            valor_nuevo=nuevo if isinstance(nuevo, str) else _serializar(nuevo),
            motivo=motivo[:255] if motivo else None,
        )
    except Exception:
        return None


class BitacoraMixin:
    """
    Registra automáticamente las operaciones de escritura de una view de DRF.

    Define 'modulo_bitacora' en la clase; si no, usa el nombre del modelo.
    """
    modulo_bitacora = None

    def _modulo(self):
        if self.modulo_bitacora:
            return self.modulo_bitacora
        modelo = getattr(getattr(self, 'queryset', None), 'model', None)
        return modelo.__name__.upper() if modelo else 'DESCONOCIDO'

    def perform_create(self, serializer):
        super().perform_create(serializer)
        registrar(self.request.user, self._modulo(), 'CREATE',
                  nuevo=serializer.instance)

    def perform_update(self, serializer):
        # Se relee de la base para tener el estado ANTES de guardar; el objeto
        # que trae el serializer ya viene con los valores nuevos aplicados.
        anterior = serializer.instance.__class__.objects.filter(
            pk=serializer.instance.pk
        ).first()
        instantanea = _serializar(anterior)

        super().perform_update(serializer)
        registrar(self.request.user, self._modulo(), 'UPDATE',
                  anterior=instantanea, nuevo=serializer.instance)

    def perform_destroy(self, instance):
        instantanea = _serializar(instance)
        # La clase de abajo decide cómo se borra: puede ser baja lógica.
        super().perform_destroy(instance)
        registrar(self.request.user, self._modulo(), 'DELETE',
                  anterior=instantanea, nuevo=instance,
                  motivo='Baja del registro')