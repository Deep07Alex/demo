from django.db import models
from django.utils import timezone

# Category model (Collections page)
class product_variety(models.Model):
    PRODUCT_TYPE_CHOICE = [
        ('NEW', 'NEW ARRIVAL'),
        ('MNG', 'MANGA & COMICS'),
        ('MRC', 'MOST READ COMBOS'),
        ('SFI', 'SELF IMPROVEMENTS'),
        ('ROS', 'ROMANCE ON SALE'),
        ('HIN', 'HINDI BOOKS'),
        ('BSM', 'BUSINESS & STOCK-MARKET'),
    ]
    
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_categories')
    date_added = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=4, choices=PRODUCT_TYPE_CHOICE, unique=True)
    
    def __str__(self):  
        return self.get_type_display()

class Product(models.Model):
    category = models.ForeignKey(product_variety, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    old_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    on_sale = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):  
        return f"{self.title} ({self.category.get_type_display()})"