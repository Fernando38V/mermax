from django.urls import path
from mermas import views

app_name = "mermas"

urlpatterns = [
    # ======================================================
    # Registro de Merma
    # ======================================================
    path("registro/list/",views.ListRegistroMermaAPIView.as_view(),name="list_registro_merma",),
    path("registro/create/",views.CreateRegistroMermaAPIView.as_view(),name="create_registro_merma",),
    path("registro/detail/<str:pk>/",views.DetailRegistroMermaAPIView.as_view(),name="detail_registro_merma",),
    path("registro/update/<str:pk>/",views.UpdateRegistroMermaAPIView.as_view(),name="update_registro_merma",),
    # ======================================================
    # Discrepancias y Recepción
    # ======================================================
    path('discrepancias/list/', views.ListDiscrepanciaAPIView.as_view(), name='list-discrepancias'),
    path('discrepancias/detail/<str:folio>/', views.DetailDiscrepanciaAPIView.as_view(), name="detail_discrepancia"),
    path("discrepancias/create/", views.DiscrepanciaCreateAPIView.as_view(), name="create_discrepancia"),
    path('discrepancias/resolver/<str:folio>/', views.ResolverDiscrepanciaAPIView.as_view(), name='resolver-discrepancia'),
    path("recepcion/confirmar/<str:folio>/", views.ConfirmarRecepcionAPIView.as_view(), name="confirmar_recepcion"),
    
    # ======================================================
    # Estaciones por linea (Para registro de nueva merma | Axel)
    # ======================================================
    path("estaciones-por-linea/", views.ListEstacionesPorLineaAPIView.as_view(), name="estaciones-por-linea"),
    path("lotes-por-componente/", views.ListLotesPorComponenteAPIView.as_view(), name="lotes-por-componente"),
    path("ordenes-por-estacion/", views.ListOrdenesPorEstacionAPIView.as_view(), name="ordenes-por-estacion"),

    #dashboard
    path("dashboard-supervisor/", views.dashboard_supervisor, name="dashboard_supervisor"),
    path("dashboard-almacen/", views.dashboard_almacen, name="dashboard_almacen"),
]   