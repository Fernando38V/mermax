from django.urls import path
from usuarios import views
from .views import LoginView, LogoutView, MeView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    
    #urls de usuarios
    path('list/', views.ListUsuarioAPIView.as_view(), name='list_usuarios'),
    path('create/', views.CreateUsuarioAPIView.as_view(), name='create_usuario'),
    path('detail/<int:pk>/', views.DetailUsuarioAPIView.as_view(), name='detail_usuario'),
    path('update/<int:pk>/', views.UpdateUsuarioAPIView.as_view(), name='update_usuario'),
    
    #urls de empleados
    path('empleado/list/', views.ListEmpleadoAPIView.as_view(), name='list_empleados'),
    path('empleado/create/', views.CreateEmpleadoAPIView.as_view(), name='create_empleado'),
    path('empleado/detail/<int:pk>/', views.DetailEmpleadoAPIView.as_view(), name='detail_empleado'),
    path('empleado/update/<int:pk>/', views.UpdateEmpleadoAPIView.as_view(), name='update_empleado'),
]

