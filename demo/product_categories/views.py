from django.shortcuts import render
from . models import *

# Create your views here.
def productcatagory(request):
    products = product_variety.objects.all().order_by('type')
    return render(request , 'pages/productcatagory.html',{'products_category': products})

def marvel_categories(request):
    comics = MarvelComic.objects.all().order_by('id')
    return render(request, 'pages/marvel_comics.html', {'comics': comics})
