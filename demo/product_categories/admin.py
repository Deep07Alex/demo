from django.contrib import admin
from .models import product_variety, Product

@admin.register(product_variety)
class ProductVarietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'date_added')
    list_filter = ('type',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'old_price', 'on_sale', 'date_added')
    list_filter = ('category', 'on_sale')
    search_fields = ('title', 'author')
    ordering = ('-date_added',)