from django.urls import path
from . import views

app_name = 'recepciones'

urlpatterns = [
    path('bandeja/', views.BandejaRecepcion.as_view(), name='bandeja'),
    path('confirmar/<str:folio>/', views.ConfirmarRecepcion.as_view(), name='confirmar'),
    path('discrepancias/', views.DiscrepanciasAbiertas.as_view(), name='discrepancias'),
    path('discrepancias/resolver/<str:folio>/', views.ResolverDiscrepancia.as_view(), name='resolver_discrepancia'),
    path('historial/', views.HistorialMovimientos.as_view(), name='historial'),
    path('disposiciones/', views.DisposicionesPendientes.as_view(), name='disposiciones'),           # ← nueva
    path('disposiciones/ejecutar/<str:folio>/', views.EjecutarDisposicion.as_view(), name='ejecutar_disposicion'),  # ← nueva
]