from django.urls import path
from . import views

urlpatterns = [
    path('api/send-verification/', views.send_verification, name='send_verification'),
    path('api/verify-token/', views.verify_token, name='verify_token'),
    path('api/resend-verification/', views.resend_verification, name='resend_verification'),
]