from django.urls import path
from inspecciones import views

app_name = 'inspecciones'

urlpatterns = [

    # urls de solicitudes de inspeccion
    path('solicitudes/list/', views.ListSolicitudInspeccionAPIView.as_view(), name='list_solicitudes'),
    path('solicitudes/iniciar/<str:codigo_solicitud>/', views.IniciarInspeccionAPIView.as_view(), name='iniciar_inspeccion'),

    # dictamen de disposicion final (RF-08, RF-09, RF-10)
    path('dictaminar/<str:codigo_solicitud>/', views.DictaminarInspeccionAPIView.as_view(), name='dictaminar'),
    path('disposicion/list/', views.ListRegistroDisposicionAPIView.as_view(), name='list_disposicion'),
    path('disposicion/ejecutar/<str:folio>/', views.EjecutarDisposicionAPIView.as_view(), name='ejecutar_disposicion'),

    # urls de devoluciones
    path('devolucion/list/', views.ListDevolucionAPIView.as_view(), name='list_devolucion'),
    path('devolucion/create/', views.CreateDevolucionAPIView.as_view(), name='create_devolucion'),
    path('devolucion/detail/<str:pk>/', views.DetailDevolucionAPIView.as_view(), name='detail_devolucion'),
    path('devolucion/update/<str:pk>/', views.UpdateDevolucionAPIView.as_view(), name='update_devolucion'),

    # urls de reciclaje
    path('reciclaje/list/', views.ListReciclajeAPIView.as_view(), name='list_reciclaje'),
    path('reciclaje/create/', views.CreateReciclajeAPIView.as_view(), name='create_reciclaje'),
    path('reciclaje/detail/<str:pk>/', views.DetailReciclajeAPIView.as_view(), name='detail_reciclaje'),
    path('reciclaje/update/<str:pk>/', views.UpdateReciclajeAPIView.as_view(), name='update_reciclaje'),

    # urls de desecho
    path('desecho/list/', views.ListDesechoAPIView.as_view(), name='list_desecho'),
    path('desecho/create/', views.CreateDesechoAPIView.as_view(), name='create_desecho'),
    path('desecho/detail/<str:pk>/', views.DetailDesechoAPIView.as_view(), name='detail_desecho'),
    path('desecho/update/<str:pk>/', views.UpdateDesechoAPIView.as_view(), name='update_desecho'),
]