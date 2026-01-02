from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "phone_number",
        "status",
        "total",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone_number", "id")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "title", "item_type", "price", "quantity")
    list_filter = ("item_type",)
    search_fields = ("title", "order__id")
