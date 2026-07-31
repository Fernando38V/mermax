from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('catalogos/', views.IndiceCatalogos.as_view(), name='catalogos_indice'),
    path('catalogos/<str:slug>/', views.ListCatalogo.as_view(), name='catalogo_list'),
    path('catalogos/<str:slug>/nuevo/', views.FormCatalogo.as_view(), name='catalogo_create'),
    path('catalogos/<str:slug>/editar/<str:pk>/', views.FormCatalogo.as_view(), name='catalogo_edit'),
    path('catalogos/<str:slug>/baja/<str:pk>/', views.BajaCatalogo.as_view(), name='catalogo_baja'),
    path('catalogos/<str:slug>/reactivar/<str:pk>/', views.ReactivarCatalogo.as_view(), name='catalogo_reactivar'),
]