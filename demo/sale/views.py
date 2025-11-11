from django.shortcuts import render
from .models import SaleBook
# Create your views here.
def sale_page(request):
    books = SaleBook.objects.all().order_by('title')
    return render(request, 'pages/sale.html', {'salebooks':books})