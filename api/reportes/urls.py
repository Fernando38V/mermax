"""
App: reportes - urls

    RF-12  GET  /api/reportes/dashboard/
    RF-11  GET  /api/reportes/trazabilidad/lote/<num>/
    RF-13  GET  /api/reportes/umbrales/
           POST /api/reportes/alertas/evaluar/
           GET  /api/reportes/alertas/
           POST /api/reportes/alertas/<num>/atender/
    RF-14  GET  /api/reportes/mermas/
           GET  /api/reportes/mermas/pdf/

Filtros disponibles en dashboard y reportes:
    ?desde=2026-05-01&hasta=2026-07-25
    ?linea=3&turno=NOC&tipo_merma=DEF_FAB&causa_raiz=CONTAM
"""
from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('trazabilidad/lote/<int:num>/',
         views.TrazabilidadLoteView.as_view(), name='trazabilidad-lote'),

    path('trazabilidad-folio/<str:folio>/', views.TrazabilidadFolioView.as_view(), name='trazabilidad-folio'),
    
    path('umbrales/', views.UmbralListView.as_view(), name='umbrales'),
    path('alertas/', views.AlertaListView.as_view(), name='alertas'),
    path('alertas/evaluar/', views.EvaluarAlertasView.as_view(), name='alertas-evaluar'),
    path('alertas/<int:num>/atender/',
         views.AtenderAlertaView.as_view(), name='alerta-atender'),

    path('mermas/', views.ReporteMermasView.as_view(), name='reporte-mermas'),
    path('mermas/pdf/', views.ReporteMermasPDFView.as_view(), name='reporte-mermas-pdf'),
]