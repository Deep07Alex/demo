from django.shortcuts import render ,get_object_or_404
from django.http import Http404
from .models import product_variety, Product

# Map type codes to models and display names
PRODUCT_CATEGORY_MAP = {
    'NEW': {'name': 'NEW ARRIVAL', 'model': Product, 'template': 'default'},
    'MNG': {'name': 'MANGA & COMICS', 'model': Product, 'template': 'comic'},
    'MRC': {'name': 'MOST READ COMBOS', 'model': Product, 'template': 'default'},
    'SFI': {'name': 'SELF IMPROVEMENTS', 'model': Product, 'template': 'default'},
    'ROS': {'name': 'ROMANCE ON SALE', 'model': Product, 'template': 'default'},
    'HIN': {'name': 'HINDI BOOKS', 'model': Product, 'template': 'default'},
    'BSM': {'name': 'BUSINESS & STOCK-MARKET', 'model': Product, 'template': 'default'},
}

def productcatagory(request):
    products = product_variety.objects.all().order_by('type')
    return render(request, 'pages/productcatagory.html', {'products_category': products})

def product_category_detail(request, category_type):
    """Show products for a specific category"""
    # Normalize the category type from URL
    category_type = category_type.upper()
    
    # Get the category object
    category = get_object_or_404(product_variety, type=category_type)
    
    # This ensures Django uses the foreign key relationship correctly
    products = Product.objects.filter(category_id=category.id).order_by('title')
    
    return render(request, 'pages/product_category_detail.html', {
        'category_name': category.get_type_display(),
        'items': products,  # This will now only contain products for THIS category
        'category_type': category_type,
    })