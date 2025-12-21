from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from homepage.models import Book
from product_categories.models import Product
from django.views.decorators.http import require_POST
import json

def search_suggestions(request):
    """Return JSON search results for live autocomplete - no duplicates"""
    query = request.GET.get('q', '').strip()
    results = []
    seen_titles = set()  # Track titles to prevent duplicates
    
    if len(query) >= 2:  
        # Search books from homepage (prioritize these)
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(category__icontains=query)
        )[:5]
        
        # Add books first
        for book in books:
            title_lower = book.title.lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                results.append({
                    'title': book.title,
                    'price': str(book.price),
                    'image': book.image.url if book.image else '',
                    'url': f"/books/{book.slug}/",
                    'type': 'Book'
                })
        
        # Search products from product_categories
        products = Product.objects.filter(
            Q(title__icontains=query) | 
            Q(category__name__icontains=query)
        )[:5]
        
        # Add products only if title hasn't been seen
        for product in products:
            title_lower = product.title.lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                results.append({
                    'title': product.title,
                    'price': str(product.price),
                    'image': product.image.url if product.image else '',
                    'url': f"/product/{product.id}/",
                    'type': 'Product'
                })
    
    return JsonResponse({'results': results})

# Cart helper functions
def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

@require_POST
def add_to_cart(request):
    """Add item to cart via AJAX"""
    try:
        data = json.loads(request.body)
        key = f"{data.get('type')}_{data.get('id')}"
        cart = get_cart(request)
        
        if key in cart:
            cart[key]['quantity'] += 1
        else:
            cart[key] = {
                'id': data.get('id'),
                'type': data.get('type'),
                'title': data.get('title'),
                'price': float(data.get('price')),
                'image': data.get('image', ''),
                'quantity': 1
            }
        
        save_cart(request, cart)
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart.values()),
            'total': sum(item['price'] * item['quantity'] for item in cart.values())
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def get_cart_items(request):
    """Get cart items for display"""
    cart = get_cart(request)
    items = list(cart.values())
    return JsonResponse({
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'items': items,
        'total': sum(item['price'] * item['quantity'] for item in cart.values())
    })

@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    data = json.loads(request.body)
    cart = get_cart(request)
    if data.get('key') in cart:
        del cart[data.get('key')]
        save_cart(request, cart)
    
    return JsonResponse({
        'success': True,
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'total': sum(item['price'] * item['quantity'] for item in cart.values())
    })

@require_POST
def update_cart_quantity(request):
    """Update item quantity"""
    data = json.loads(request.body)
    cart = get_cart(request)
    key = data.get('key')
    
    if key in cart:
        quantity = int(data.get('quantity', 1))
        if quantity <= 0:
            del cart[key]
        else:
            cart[key]['quantity'] = quantity
        save_cart(request, cart)
    
    return JsonResponse({
        'success': True,
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'total': sum(item['price'] * item['quantity'] for item in cart.values())
    })

def search(request):
    """Handle search page requests"""
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # Search books
        book_results = Book.objects.filter(
            Q(title__icontains=query) | Q(category__icontains=query)
        )
        
        # Search products
        product_results = Product.objects.filter(
            Q(title__icontains=query) | Q(category__name__icontains=query)
        )
        
        # Combine results
        results = list(book_results) + list(product_results)
    
    return render(request, 'pages/search_results.html', {
        'query': query,
        'results': results
    })
    
def checkout(request):

    cart = get_cart(request)    
    
    # Convert cart dict values to list for template iteration
    cart_items = list(cart.values())
    
    # Calculate totals
    subtotal = sum(float(item['price']) * item['quantity'] for item in cart_items)
    shipping = 49.00  # Flat rate shipping
    total = subtotal + shipping
    
    # Add initials for placeholder images if image is missing
    for item in cart_items:
        if not item.get('image'):
            # Create initials from first letters of first two words
            words = item['title'].split()
            item['initials'] = ''.join([word[0].upper() for word in words[:2]])
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    }
    
    return render(request, 'pages/payment.html', context)

def home_page(request):
    return render(request, 'index.html')

def Aboutus(request):
    return render(request, 'pages/Aboutus.html')

def contact_information(request):
    return render(request, 'pages/contactinformation.html')