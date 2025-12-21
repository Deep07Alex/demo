from django.urls import path
from . import views

urlpatterns = [
    path('api/send-otp/', views.send_otp, name='send_otp'),
    path('api/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/resend-otp/', views.resend_otp, name='resend_otp'),
    path('api/save-order/', views.save_order, name='save_order'),
]