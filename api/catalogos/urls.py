from django.urls import path
from catalogos import views

app_name = 'catalogos'

urlpatterns = [
    #urls de empresas recicladoras
    path('recicladora/list/', views.ListRecicladoraAPIView.as_view(), name='list_recicladoras'),
    path('recicladora/create/', views.CreateRecicladoraAPIView.as_view(), name='create_recicladora'),
    path('recicladora/detail/<str:pk>/', views.DetailRecicladoraAPIView.as_view(), name='detail_recicladora'),
    path('recicladora/update/<str:pk>/', views.UpdateRecicladoraAPIView.as_view(), name='update_recicladora'),
    
    #urls de metodos de destruccion
    path('metodo/list/', views.ListMetodoAPIView.as_view(), name='list_metodos'),
    path('metodo/create/', views.CreateMetodoAPIView.as_view(), name='create_metodo'),
    path('metodo/detail/<str:pk>/', views.DetailMetodoAPIView.as_view(), name='detail_metodo'),
    path('metodo/update/<str:pk>/', views.UpdateMetodoAPIView.as_view(), name='update_metodo'),
    
]