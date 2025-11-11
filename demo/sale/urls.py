from django.urls import path 
from . import views


urlpatterns = [
   path('', views.sale_page, name='sale'),
]