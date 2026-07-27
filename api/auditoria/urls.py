"""
App: auditoria - urls
RF-47. Sólo métodos GET: la bitácora no se escribe ni se borra desde la API.

    GET /api/auditoria/bitacora/
    GET /api/auditoria/bitacora/<num>/
    GET /api/auditoria/resumen/
"""
from django.urls import path

from . import views

urlpatterns = [
    path('bitacora/', views.BitacoraListView.as_view(), name='bitacora'),
    path('bitacora/<int:num>/', views.BitacoraDetailView.as_view(), name='bitacora-detalle'),
    path('resumen/', views.BitacoraResumenView.as_view(), name='bitacora-resumen'),
]