"""
App: catalogos - views

Estructura:

- CatalogoLecturaView      lista de sólo lectura, para llenar los combos
- CatalogoAdminViewSet     CRUD completo con baja lógica, para los 6 catálogos
                           que los RF piden administrar

La baja lógica está centralizada en BajaLogicaMixin: el método DELETE nunca
borra la fila, cambia 'activo' a False. Los RF-18, 22, 26, 30, 38 y 42 lo
piden explícitamente para no perder la trazabilidad del scrap histórico.

Control de acceso: la clase SoloAdministrador aplica el RNF-02. Los catálogos
se pueden CONSULTAR desde cualquier rol (el Supervisor necesita ver las causas
raíz para registrar una merma, RF-37), pero sólo el Administrador puede
crearlos, editarlos o darlos de baja.
"""
from rest_framework import filters, permissions, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from . import serializers as s
from .models import (
    Almacen, Area, CausaRaiz, Componente, DisposicionFinal, EdoFlujoMerma,
    EdoSolicitud, EmpresaRecicladora, EstacionTrabajo, EstadoAlerta,
    EstadoDisposicion, EstadoLinea, EstadoLote, EstadoOrden, IndicadorKpi,
    LineaProduccion, MetodoDestruccion, Planta, Producto, Proveedor, Rol,
    TipoMerma, Turno,
)


# ======================================================
# Permisos (RNF-02: control de acceso por rol)
# ======================================================

class SoloAdministrador(permissions.BasePermission):
    """
    Lectura para cualquier usuario autenticado; escritura sólo para ADMIN.
    """
    message = 'Sólo el Administrador puede modificar los catálogos.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.rol_id == 'ADMIN'


# ======================================================
# Bases reutilizables
# ======================================================

class BajaLogicaMixin:
    """
    Convierte el DELETE en una baja lógica.
    'campo_baja' es el nombre del campo que marca la inactividad.
    """
    campo_baja = 'activo'

    def destroy(self, request, *args, **kwargs):
        objeto = self.get_object()
        setattr(objeto, self.campo_baja, False)
        objeto.save(update_fields=[self.campo_baja])
        return Response(
            {'detail': 'Registro dado de baja. Su historial se conserva.'},
            status=status.HTTP_200_OK,
        )


class CatalogoAdminViewSet(BajaLogicaMixin, viewsets.ModelViewSet):
    """
    CRUD estándar de un catálogo administrable.
    Trae buscador de texto y filtro por estado activo/inactivo, que es lo que
    piden los RF de consulta (RF-17, 21, 25, 29, 37, 41).
    """
    permission_classes = [SoloAdministrador]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        qs = self.queryset
        activo = self.request.query_params.get('activo')
        if activo is not None:
            qs = qs.filter(activo=activo.lower() in ('1', 'true', 'si', 'sí'))
        return qs


class CatalogoLecturaView(ListAPIView):
    """Catálogo de sólo lectura: sirve para llenar combos en los formularios."""
    permission_classes = [permissions.IsAuthenticated]


# ======================================================
# RF-15 a RF-18: Líneas de producción
# ======================================================

class LineaProduccionViewSet(CatalogoAdminViewSet):
    queryset = LineaProduccion.objects.select_related('area', 'estado_linea').all()
    serializer_class = s.LineaProduccionSerializer
    search_fields = ['nombre', 'descripcion']  # numero_linea es entero: SearchFilter usa icontains y trona
    ordering_fields = ['numero_linea', 'nombre']
    ordering = ['numero_linea']

    def get_queryset(self):
        # La línea no usa 'activo': su baja se marca en estado_linea
        qs = self.queryset
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado_linea=estado.upper())
        return qs

    def destroy(self, request, *args, **kwargs):
        """RF-18: la baja cambia el estado de la línea a INACTIVA."""
        linea = self.get_object()
        linea.estado_linea_id = 'INACTIVA'
        linea.save(update_fields=['estado_linea'])
        return Response(
            {'detail': 'Línea marcada como Inactiva. No podrá seleccionarse en nuevos registros.'},
            status=status.HTTP_200_OK,
        )


# ======================================================
# RF-19 a RF-22: Componentes o piezas
# ======================================================

class ComponenteViewSet(CatalogoAdminViewSet):
    queryset = Componente.objects.all()
    serializer_class = s.ComponenteSerializer
    search_fields = ['codigo', 'nombre', 'descripcion', 'tipo']
    ordering_fields = ['codigo', 'nombre', 'costo']
    ordering = ['codigo']


# ======================================================
# RF-23 a RF-26: Proveedores
# ======================================================

class ProveedorViewSet(CatalogoAdminViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = s.ProveedorSerializer
    search_fields = ['codigo', 'nombre', 'rfc', 'correo']
    ordering_fields = ['codigo', 'nombre']
    ordering = ['nombre']


# ======================================================
# RF-27 a RF-30: Estaciones de trabajo
# ======================================================

class EstacionTrabajoViewSet(CatalogoAdminViewSet):
    queryset = EstacionTrabajo.objects.select_related('linea_produccion').all()
    serializer_class = s.EstacionTrabajoSerializer
    search_fields = ['codigo', 'nombre', 'etapa']
    ordering_fields = ['codigo', 'nombre']
    ordering = ['codigo']

    def get_queryset(self):
        """RF-29: el Supervisor y el Administrador filtran por línea."""
        qs = super().get_queryset()
        linea = self.request.query_params.get('linea')
        if linea:
            qs = qs.filter(linea_produccion=linea)
        return qs


# ======================================================
# RF-35 a RF-38: Causas raíz
# ======================================================

class CausaRaizViewSet(CatalogoAdminViewSet):
    queryset = CausaRaiz.objects.all()
    serializer_class = s.CausaRaizSerializer
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['nombre']


# ======================================================
# RF-39 a RF-42: Tipos de merma
# ======================================================

class TipoMermaViewSet(CatalogoAdminViewSet):
    queryset = TipoMerma.objects.all()
    serializer_class = s.TipoMermaSerializer
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['nombre']


# ======================================================
# Catálogos de apoyo de los dictámenes (RF-09 y RF-10)
# ======================================================

class EmpresaRecicladoraViewSet(CatalogoAdminViewSet):
    queryset = EmpresaRecicladora.objects.all()
    serializer_class = s.EmpresaRecicladoraSerializer
    search_fields = ['codigo', 'nombre']
    ordering = ['nombre']


class MetodoDestruccionViewSet(CatalogoAdminViewSet):
    queryset = MetodoDestruccion.objects.all()
    serializer_class = s.MetodoDestruccionSerializer
    search_fields = ['codigo', 'nombre']
    ordering = ['nombre']


# ======================================================
# Catálogos de sólo lectura
# ======================================================

class EstadoLineaListView(CatalogoLecturaView):
    queryset = EstadoLinea.objects.all()
    serializer_class = s.EstadoLineaSerializer


class EstadoOrdenListView(CatalogoLecturaView):
    queryset = EstadoOrden.objects.all()
    serializer_class = s.EstadoOrdenSerializer


class EstadoLoteListView(CatalogoLecturaView):
    queryset = EstadoLote.objects.all()
    serializer_class = s.EstadoLoteSerializer


class EstadoAlertaListView(CatalogoLecturaView):
    queryset = EstadoAlerta.objects.all()
    serializer_class = s.EstadoAlertaSerializer


class EstadoDisposicionListView(CatalogoLecturaView):
    queryset = EstadoDisposicion.objects.all()
    serializer_class = s.EstadoDisposicionSerializer


class EdoFlujoMermaListView(CatalogoLecturaView):
    queryset = EdoFlujoMerma.objects.all()
    serializer_class = s.EdoFlujoMermaSerializer


class EdoSolicitudListView(CatalogoLecturaView):
    queryset = EdoSolicitud.objects.all()
    serializer_class = s.EdoSolicitudSerializer


class DisposicionFinalListView(CatalogoLecturaView):
    queryset = DisposicionFinal.objects.all()
    serializer_class = s.DisposicionFinalSerializer


class RolListView(CatalogoLecturaView):
    queryset = Rol.objects.all()
    serializer_class = s.RolSerializer


class TurnoListView(CatalogoLecturaView):
    queryset = Turno.objects.all()
    serializer_class = s.TurnoSerializer


class IndicadorKpiListView(CatalogoLecturaView):
    queryset = IndicadorKpi.objects.all()
    serializer_class = s.IndicadorKpiSerializer


class PlantaListView(CatalogoLecturaView):
    queryset = Planta.objects.all()
    serializer_class = s.PlantaSerializer


class AreaListView(CatalogoLecturaView):
    queryset = Area.objects.select_related('planta').all()
    serializer_class = s.AreaSerializer


class AlmacenListView(CatalogoLecturaView):
    queryset = Almacen.objects.all()
    serializer_class = s.AlmacenSerializer


class ProductoListView(CatalogoLecturaView):
    queryset = Producto.objects.all()
    serializer_class = s.ProductoSerializer