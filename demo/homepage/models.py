from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Book(models.Model):
    CATEGORY_CHOICES = [
        ('new_arrivals', 'NEW ARRIVALS'),
        ('manga_comics', 'MANGA & COMICS'),
        ('most_read_combos', 'MOST READ COMBOS'),
        ('self_improvements', 'SELF IMPROVEMENTS'),
        ('romance', 'ROMANCE ON SALE'),
        ('hindi', 'HINDI BOOKS'),
        ('business_stock_market', 'BUSINESS & STOCK-MARKET'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    old_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='book_images_homepage/')
    on_sale = models.BooleanField(default=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='self_help')
    date_added = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self): 
        return self.title