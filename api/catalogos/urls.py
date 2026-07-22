from django.urls import path
from catalogos import views

app_name = 'catalogos'

urlpatterns = [
    path('recicladora/list/', views.ListRecicladoraAPIView.as_view(), name='list_recicladoras'),
    path('recicladora/create/', views.CreateRecicladoraAPIView.as_view(), name='create_recicladora'),
    path('recicladora/detail/<str:pk>/', views.DetailRecicladoraAPIView.as_view(), name='detail_recicladora'),
    path('recicladora/update/<str:pk>/', views.UpdateRecicladoraAPIView.as_view(), name='update_recicladora'),
]