from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("homepage.urls")),
    path('productcatagory/', include("product_categories.urls")),
    path('aboutus/', views.Aboutus, name="aboutus"),
    path('contactinformation/', views.contact_information, name="contactinformation"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

