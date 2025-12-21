from django.contrib import admin
from .models import PhoneVerification, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_type', 'item_id', 'title', 'price', 'quantity', 'image_url')

@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'delivery_method', 'is_verified', 'created_at', 'expires_at')
    list_filter = ('delivery_method', 'is_verified', 'created_at')
    search_fields = ('phone_number', 'otp')
    readonly_fields = ('otp', 'expires_at')
    
    def has_add_permission(self, request):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'full_name', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('phone_number', 'full_name', 'email')
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]
    
    def has_add_permission(self, request):
        return False

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'price', 'quantity', 'item_type')
    list_filter = ('item_type',)
    search_fields = ('title',)
    readonly_fields = ('order', 'item_type', 'item_id', 'title', 'price', 'quantity', 'image_url')
    
    def has_add_permission(self, request):
        return False