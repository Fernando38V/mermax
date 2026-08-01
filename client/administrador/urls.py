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

    path('usuarios/', views.ListUsuarios.as_view(), name='usuarios_list'),
    path('usuarios/nuevo/', views.FormUsuario.as_view(), name='usuario_create'),
    path('usuarios/editar/<int:pk>/', views.FormUsuario.as_view(), name='usuario_edit'),

    path('empleados/', views.ListEmpleados.as_view(), name='empleados_list'),
    path('empleados/nuevo/', views.FormEmpleado.as_view(), name='empleado_create'),
    path('empleados/editar/<int:pk>/', views.FormEmpleado.as_view(), name='empleado_edit'),

    path('personal/nuevo/', views.AltaPersonal.as_view(), name='personal_create'),
]