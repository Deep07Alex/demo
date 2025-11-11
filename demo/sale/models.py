from django.db import models

class SaleBook(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='sale_books/')
    old_price = models.DecimalField(max_digits=8, decimal_places=2)
    new_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_on_sale = models.BooleanField(default=True)

    def __str__(self):
        return self.title
