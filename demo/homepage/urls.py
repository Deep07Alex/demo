from django.urls import path , include
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('books/<slug:slug>/', views.book_detail, name='book_detail'),
    path('sale/', include('sale.urls')),
]