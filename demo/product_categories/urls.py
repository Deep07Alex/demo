from django.urls import path 
from . import views


urlpatterns = [
   path('',views.productcatagory , name="productcatagory"),
    path('marvel-comics/', views.marvel_categories, name='marvel_comics'),
]