from django.urls import path
from . import views

app_name = 'reportes' 

urlpatterns = [
    path('dashboard/', views.dashboard_kpis, name='dashboard_kpis'),
    path('alertas/', views.lista_alertas, name='alertas_umbral'),
    path('alertas/evaluar/', views.evaluar_alertas, name='evaluar_alertas'),
    path('alertas/<int:num>/atender/', views.atender_alerta, name='atender_alerta'),
    path('umbrales/configurar/', views.configurar_umbrales_view, name='configurar_umbrales'),
    path('mermas/', views.reporte_mermas, name='reporte-mermas'),
    path('mermas/pdf/', views.exportar_reporte_pdf, name='exportar-pdf'),
]