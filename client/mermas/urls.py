from django.urls import path

from . import views

app_name = 'mermas'

urlpatterns = [
    path('list/', views.ListMermas.as_view(), name='list_mermas'),
]