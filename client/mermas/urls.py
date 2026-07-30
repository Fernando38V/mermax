from django.urls import path

from . import views

app_name = 'mermas'

urlpatterns = [
    path('list/', views.ListMermas.as_view(), name='list_mermas'),
    path('create/', views.CreateMermas.as_view(), name='create_mermas'),
    path('estaciones-por-linea/', views.EstacionesPorLinea.as_view(), name='estaciones_por_linea'),
    path('lotes-por-componente/', views.LotesPorComponente.as_view(), name='lotes_por_componente'),
    path('ordenes-por-estacion/', views.OrdenesPorEstacion.as_view(), name='ordenes_por_estacion'),
]