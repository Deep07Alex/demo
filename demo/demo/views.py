from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.http import require_POST
from homepage.models import Book
from product_categories.models import Product
import json

def normalize_title(title):
    return title.lower().strip().replace(' ', '_')

def search_suggestions(request):
    """Return JSON search results for live autocomplete - no duplicates"""
    query = request.GET.get('q', '').strip()
    results = []
    seen_titles = set()
    
    if len(query) >= 2:
        # Search books from homepage
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(category__icontains=query)
        )[:5]
        
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

def buy_now(request, book_id):
    """Add a single book to cart and redirect to checkout"""
    book = get_object_or_404(Book, id=book_id)
    
    cart = {}
    key = f"book_{book.id}"
    cart[key] = {
        'id': book.id,
        'type': 'book',
        'title': book.title,
        'price': str(book.price),
        'image': book.image.url if book.image else '',
        'quantity': 1
    }
    request.session['cart'] = cart
    request.session.modified = True
    
    return redirect('checkout')

def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

@require_POST
def clear_cart(request):
    """Clear all items from cart"""
    request.session['cart'] = {}
    request.session.modified = True
    return JsonResponse({'success': True})

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

@require_POST
def update_cart_addons(request):
    """Update cart add-ons selection"""
    try:
        data = json.loads(request.body)
        addons = data.get('addons', {})
        request.session['cart_addons'] = addons
        request.session.modified = True
        
        addon_prices = {'Bag': 30, 'bookmark': 20, 'packing': 20}
        addon_total = sum(addon_prices.get(key, 0) for key, selected in addons.items() if selected)
        
        return JsonResponse({
            'success': True,
            'addon_total': addon_total
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def get_cart_addons(request):
    """Get cart add-ons and their total"""
    addons = request.session.get('cart_addons', {})
    addon_prices = {'Bag': 30, 'bookmark': 20, 'packing': 20}
    addon_total = sum(addon_prices.get(key, 0) for key, selected in addons.items() if selected)
    
    return JsonResponse({
        'addons': addons,
        'addon_total': addon_total
    })

def get_cart_items(request):
    """Get cart items for display"""
    cart = get_cart(request)
    items = list(cart.values())
    
    addons = request.session.get('cart_addons', {})
    addon_prices = {'Bag': 30, 'bookmark': 20, 'packing': 20}
    addon_total = sum(addon_prices.get(key, 0) for key, selected in addons.items() if selected)
    
    # Smart pricing
    total_books = sum(item['quantity'] for item in cart.values())
    product_total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    
    shipping = 0 if product_total >= 499 else 49.00
    discount = 100 if total_books >= 10 else 0
    
    total = product_total + shipping + addon_total - discount
    
    return JsonResponse({
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'items': items,
        'addon_total': addon_total,
        'shipping': shipping,
        'discount': discount,
        'total': total,
        'total_books': total_books,
    })

@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    try:
        data = json.loads(request.body)
        cart = get_cart(request)
        key = data.get('key')
        
        if not key:
            return JsonResponse({'success': False, 'error': 'No key provided'}, status=400)
        
        if key in cart:
            del cart[key]
            save_cart(request, cart)
        else:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart.values()),
            'total': sum(item['price'] * item['quantity'] for item in cart.values())
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_POST
def update_cart_quantity(request):
    """Update item quantity"""
    try:
        data = json.loads(request.body)
        cart = get_cart(request)
        key = data.get('key')
        
        if not key:
            return JsonResponse({'success': False, 'error': 'No key provided'}, status=400)
        
        if key in cart:
            quantity = int(data.get('quantity', 1))
            if quantity <= 0:
                del cart[key]
            else:
                cart[key]['quantity'] = quantity
            save_cart(request, cart)
        else:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart.values()),
            'total': sum(item['price'] * item['quantity'] for item in cart.values())
        })
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def search(request):
    """Handle search page requests"""
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        book_results = Book.objects.filter(
            Q(title__icontains=query) | Q(category__icontains=query)
        )
        
        product_results = Product.objects.filter(
            Q(title__icontains=query) | Q(category__name__icontains=query)
        )
        
        results = list(book_results) + list(product_results)
    
    return render(request, 'pages/search_results.html', {
        'query': query,
        'results': results
    })


def home_page(request):
    return render(request, 'index.html')

def Aboutus(request):
    return render(request, 'pages/Aboutus.html')

def contact_information(request):
    return render(request, 'pages/contactinformation.html')

def bulk_purchase(request):
    return render(request, 'pages/bulk.html')