# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('books/<slug:slug>/', views.book_detail, name='book_detail'),
    
    # Existing category pages
    path('sale/', views.sale_page, name='sale'),
    path('romance/', views.romance_page, name='romance'),
    path('trading-finance/', views.trading_finance_page, name='trading-finance'),
    path('manga/', views.manga_page, name='manga'),
    path('robert-greene-special/', views.robert_greene_special_page, name='robert-greene-special'),
    path('mythology/', views.mythology_page, name='mythology'),
    path('hindi-books/', views.hindi_books_page, name='hindi-books'),
    path('preloved-bestsellers/', views.preloved_bestsellers_page, name='preloved-bestsellers'),
    path('new-arrivals/', views.new_arrivals_page, name='new-arrivals'),
]