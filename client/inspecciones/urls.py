from django.urls import path
from . import views

app_name = 'inspecciones'

urlpatterns = [
    path('alertas/', views.AlertasInspeccion.as_view(), name='alertas'),
    path('solicitudes/iniciar/<str:codigo_solicitud>/', views.IniciarInspeccion.as_view(), name='iniciar_inspeccion'),
    path('', views.DictaminarInspeccion.as_view(), name='dictaminar_inspeccion'),
    path('<str:codigo_solicitud>/', views.DictaminarInspeccion.as_view(), name='dictaminar_inspeccion_codigo'),
]