from django.urls import path
from recepciones.views import (
    RecepcionesPendientesListView, ConfirmarRecepcionAPIView,
    DiscrepanciaCreateAPIView, ResolverDiscrepanciaAPIView
)

urlpatterns = [
    path('bandeja/', RecepcionesPendientesListView.as_view(), name='bandeja'),
    path('confirmar/', ConfirmarRecepcionAPIView.as_view(), name='confirmar'),
    path('discrepancias/crear/', DiscrepanciaCreateAPIView.as_view(), name='crear-discrepancia'),
    path('discrepancias/<str:folio_discrepancia>/resolver/', ResolverDiscrepanciaAPIView.as_view(), name='resolver-discrepancia'),
]