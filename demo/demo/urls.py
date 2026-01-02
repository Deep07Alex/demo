from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from . import views as demo_views
from user import views as user_views

urlpatterns = [
    path(
        'webhook/shiprocket/',
        csrf_exempt(user_views.shiprocket_webhook),
        name='shiprocket_webhook',
    ),

    # ==================== HOMEPAGE & PAGES ====================
    path('', include("homepage.urls")),
    path('aboutus/', demo_views.Aboutus, name="aboutus"),
    path('contactinformation/', demo_views.contact_information, name="contactinformation"),
    path('search/', demo_views.search, name="search"),
    path('search/suggestions/', demo_views.search_suggestions, name='search_suggestions'),
    path('return/', demo_views.return_policy, name="return_policy"),
    path('privacy-policy/', demo_views.privacy_policy, name="privacy_policy"),

    path('books/<slug:slug>/', demo_views.book_detail, name='book_detail'),
    path('category/<str:category>/', demo_views.category_books, name='category_books'),
    path('bulkpurchase/', demo_views.bulk_purchase, name='bulk_purchase'),
    path('buy-now/<int:book_id>/', demo_views.buy_now, name='buy_now'),

    # ==================== PRODUCT CATEGORIES ====================
    path('productcatagory/', include("product_categories.urls")),

    # ==================== CART & CHECKOUT ====================
    path('cart/', include('user.urls')),
    path('checkout/', user_views.checkout, name='checkout'),
    path('api/', include('user.urls')),

    # ==================== PAYMENT ====================
    path('payment/success/', user_views.payment_success, name='payment_success'),
    path('payment/failure/', user_views.payment_failure, name='payment_failure'),

    # ==================== ADMIN ====================
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
