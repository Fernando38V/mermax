from django.urls import path
from . import views

app_name = 'reportes' 

urlpatterns = [
    # Vista principal del panel de alertas en el navegador
    path('alertas/', views.lista_alertas, name='alertas_umbral'),
    
    # Acciones POST que el cliente ejecuta hacia la API
    path('alertas/evaluar/', views.evaluar_alertas, name='evaluar_alertas'),
    path('alertas/<int:num>/atender/', views.atender_alerta, name='atender_alerta'),
]