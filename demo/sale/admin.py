from django.contrib import admin
from .models import SaleBook

@admin.register(SaleBook)
class SaleBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'old_price', 'new_price', 'is_on_sale')
    list_filter = ('is_on_sale',)
    search_fields = ('title',)
    ordering = ('title',)
    list_editable = ('is_on_sale', 'new_price')
    list_per_page = 10 

    fieldsets = (
        ("Book Information", {
            'fields': ('title', 'image')
        }),
        ("Pricing Details", {
            'fields': ('new_price', 'old_price', 'is_on_sale'),
        }),
    )
