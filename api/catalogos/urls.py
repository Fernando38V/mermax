"""
App: catalogos - urls

Los 6 catálogos administrables usan DefaultRouter, que genera solo las
rutas estándar de un CRUD:

    GET    /api/catalogos/componentes/          lista        RF-21
    POST   /api/catalogos/componentes/          alta         RF-19
    GET    /api/catalogos/componentes/COMP-01/  detalle      RF-21
    PUT    /api/catalogos/componentes/COMP-01/  edición      RF-20
    PATCH  /api/catalogos/componentes/COMP-01/  edición parcial
    DELETE /api/catalogos/componentes/COMP-01/  baja lógica  RF-22

Parámetros de consulta disponibles en los 6:
    ?search=texto     buscador (RF-17, 21, 25, 29, 37, 41)
    ?activo=false     filtra por estado
    ?ordering=nombre  orden

Los catálogos de sólo lectura van como rutas sueltas bajo /lookup/, para
dejar claro que existen nada más para llenar combos.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('lineas', views.LineaProduccionViewSet, basename='linea')
router.register('componentes', views.ComponenteViewSet, basename='componente')
router.register('proveedores', views.ProveedorViewSet, basename='proveedor')
router.register('estaciones', views.EstacionTrabajoViewSet, basename='estacion')
router.register('causas-raiz', views.CausaRaizViewSet, basename='causa-raiz')
router.register('tipos-merma', views.TipoMermaViewSet, basename='tipo-merma')
router.register('empresas-recicladoras', views.EmpresaRecicladoraViewSet, basename='empresa-recicladora')
router.register('metodos-destruccion', views.MetodoDestruccionViewSet, basename='metodo-destruccion')

urlpatterns = [
    path('', include(router.urls)),

    # Catálogos de sólo lectura (combos de formularios)
    path('lookup/estados-linea/', views.EstadoLineaListView.as_view(), name='lk-estado-linea'),
    path('lookup/estados-orden/', views.EstadoOrdenListView.as_view(), name='lk-estado-orden'),
    path('lookup/estados-lote/', views.EstadoLoteListView.as_view(), name='lk-estado-lote'),
    path('lookup/estados-alerta/', views.EstadoAlertaListView.as_view(), name='lk-estado-alerta'),
    path('lookup/estados-disposicion/', views.EstadoDisposicionListView.as_view(), name='lk-estado-disposicion'),
    path('lookup/estados-flujo/', views.EdoFlujoMermaListView.as_view(), name='lk-edo-flujo'),
    path('lookup/estados-solicitud/', views.EdoSolicitudListView.as_view(), name='lk-edo-solicitud'),
    path('lookup/disposiciones-final/', views.DisposicionFinalListView.as_view(), name='lk-disposicion-final'),
    path('lookup/roles/', views.RolListView.as_view(), name='lk-rol'),
    path('lookup/turnos/', views.TurnoListView.as_view(), name='lk-turno'),
    path('lookup/indicadores-kpi/', views.IndicadorKpiListView.as_view(), name='lk-kpi'),
    path('lookup/plantas/', views.PlantaListView.as_view(), name='lk-planta'),
    path('lookup/areas/', views.AreaListView.as_view(), name='lk-area'),
    path('lookup/almacenes/', views.AlmacenListView.as_view(), name='lk-almacen'),
    path('lookup/productos/', views.ProductoListView.as_view(), name='lk-producto'),
]