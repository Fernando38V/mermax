from django.urls import path
from mermas import views

app_name = "mermas"

urlpatterns = [

    path("registro/list/",views.ListRegistroMermaAPIView.as_view(),name="list_registro_merma",),
    path("registro/create/",views.CreateRegistroMermaAPIView.as_view(),name="create_registro_merma",),
    path("registro/detail/<str:pk>/",views.DetailRegistroMermaAPIView.as_view(),name="detail_registro_merma",),
    path("registro/update/<str:pk>/",views.UpdateRegistroMermaAPIView.as_view(),name="update_registro_merma",),
    
]