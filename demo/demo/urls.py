from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("homepage.urls")),
    path('productcatagory/', include("product_categories.urls")),
    path('aboutus/', views.Aboutus, name="aboutus"),
    path('contactinformation/', views.contact_information, name="contactinformation"),
    path('search/', views.search, name="search"),
    path('search/suggestions/', views.search_suggestions, name="search_suggestions"),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/items/', views.get_cart_items, name='get_cart_items'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)