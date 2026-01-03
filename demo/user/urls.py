from django.urls import path

from . import views

urlpatterns = [

    # ============ EMAIL VERIFICATION ============

    path("api/send-email-otp/", views.send_email_otp, name="send_email_otp"),

    path("api/verify-email-otp/", views.verify_email_otp, name="verify_email_otp"),

    # ============ CART OPERATIONS ============

    path("cart/clear/", views.clear_cart, name="clear_cart"),

    path("cart/add/", views.add_to_cart, name="add_to_cart"),

    path("cart/addons/update/", views.update_cart_addons, name="update_cart_addons"),

    path("cart/addons/get/", views.get_cart_addons, name="get_cart_addons"),

    path("cart/items/", views.get_cart_items, name="get_cart_items"),

    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),

    path("cart/update/", views.update_cart_quantity, name="update_cart_quantity"),

    # ============ CHECKOUT & PAYMENT PAGES ============

    path("checkout/", views.checkout, name="checkout"),

    path("payment/redirect/", views.payment_redirect, name="payment_redirect"),
    
    path("api/check-checkout-lock/", views.check_checkout_lock, name="check_checkout_lock"),

    path("payment/success/", views.payment_success, name="payment_success"),

    path("payment/failure/", views.payment_failure, name="payment_failure"),

    # ============ PAYMENT & SHIPPING APIS ============

    path("api/initiate-payment/", views.initiate_payu_payment,
         name="initiate_payu_payment"),

    path("api/place-cod-order/", views.place_cod_order,
         name="place_cod_order"),

    path("api/calculate-shipping/", views.calculate_shipping,
         name="calculate_shipping"),

]