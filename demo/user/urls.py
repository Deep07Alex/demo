from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    # ==================== WEBHOOKS ====================
    path(
        "webhook/shiprocket/",
        csrf_exempt(views.shiprocket_webhook),
        name="shiprocket_webhook",
    ),

    # Email verification
    path("send-email-otp/", views.send_email_otp, name="send_email_otp"),
    path("verify-email-otp/", views.verify_email_otp, name="verify_email_otp"),

    # Cart operations
    path("clear/", views.clear_cart, name="clear_cart"),
    path("add/", views.add_to_cart, name="add_to_cart"),
    path("addons/update/", views.update_cart_addons, name="update_cart_addons"),
    path("addons/get/", views.get_cart_addons, name="get_cart_addons"),
    path("items/", views.get_cart_items, name="get_cart_items"),
    path("remove/", views.remove_from_cart, name="remove_from_cart"),
    path("update/", views.update_cart_quantity, name="update_cart_quantity"),

    # Payment & Shipping
    path("initiate-payment/", views.initiate_payu_payment, name="initiate_payu_payment"),
    path("calculate-shipping/", views.calculate_shipping, name="calculate_shipping"),
]
