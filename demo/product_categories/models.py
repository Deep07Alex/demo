from django.db import models as mod
from django.utils import timezone

class product_variety(mod.Model):
    PRODUCT_TYPE_CHOICE = [
        ('LAFK','Learning Apps For Kids'),
        ('PF', 'Popular Fictions'),
        ('AAL', 'All About Love'),
        ('MG', 'Manga Club'),
        ('NA', 'New Arrivals'),
        ('MC', 'Marvel Comics'),
        ('DC', 'DC Comics'),
        ('RF', 'Romance & Fictions'),
        ('KB', 'Kids Books'),
        ('MT', 'Mythology & Tails')
    ]
    
    name = mod.CharField(max_length=100)
    image = mod.ImageField(upload_to='product_categories')
    date_added = mod.DateTimeField(default=timezone.now)
    type = mod.CharField(max_length=4,choices=PRODUCT_TYPE_CHOICE)
    
    def __str__(self):
        return self.name
    


class MarvelComic(mod.Model):
    title = mod.CharField(max_length=200)
    author = mod.CharField(max_length=100, blank=True, null=True)
    description = mod.TextField(blank=True, null=True)
    price = mod.DecimalField(max_digits=6, decimal_places=2)
    image = mod.ImageField(upload_to='marvel_comics/', blank=True, null=True)
    date_added = mod.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
