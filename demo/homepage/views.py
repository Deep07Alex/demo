# home/views.py
from django.shortcuts import render, get_object_or_404
from .models import Book

def home_page(request):
    context = {
        'sale_books': Book.objects.filter(category='self_help', on_sale=True).order_by('title'),
        'romance_books': Book.objects.filter(category='romance').order_by('title'),
        'trading_finance_books': Book.objects.filter(category='trading_finance').order_by('title'),
        'manga_books': Book.objects.filter(category='manga').order_by('title'),
        'robert_greene_special_books': Book.objects.filter(category='robert_greene_special').order_by('title'),
        'mythology_books': Book.objects.filter(category='mythology').order_by('title'),
        'hindi_books': Book.objects.filter(category='hindi').order_by('title'),
        'preloved_bestsellers_books': Book.objects.filter(category='preloved_bestsellers').order_by('title'),
        'new_arrivals_books': Book.objects.filter(category='new_arrivals').order_by('title'),
    }
    return render(request, 'index.html', context)

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    return render(request, 'book_detail.html', {'book': book})

# Existing views
def sale_page(request):
    books = Book.objects.filter(category='self_help', on_sale=True).order_by('title')
    return render(request, 'pages/sale.html', {'books': books})

def romance_page(request):
    books = Book.objects.filter(category='romance').order_by('title')
    return render(request, 'pages/romance.html', {'books': books})

def trading_finance_page(request):
    books = Book.objects.filter(category='trading_finance').order_by('title')
    return render(request, 'pages/trading_finance.html', {'books': books})

def manga_page(request):
    books = Book.objects.filter(category='manga').order_by('title')
    return render(request, 'pages/manga.html', {'books': books})

# NEW view functions
def robert_greene_special_page(request):
    books = Book.objects.filter(category='robert_greene_special').order_by('title')
    return render(request, 'pages/robert_greene_special.html', {'books': books})

def mythology_page(request):
    books = Book.objects.filter(category='mythology').order_by('title')
    return render(request, 'pages/mythology.html', {'books': books})

def hindi_books_page(request):
    books = Book.objects.filter(category='hindi').order_by('title')
    return render(request, 'pages/hindi_books.html', {'books': books})

def preloved_bestsellers_page(request):
    books = Book.objects.filter(category='preloved_bestsellers').order_by('title')
    return render(request, 'pages/preloved_bestsellers.html', {'books': books})

def new_arrivals_page(request):
    books = Book.objects.filter(category='new_arrivals').order_by('title')
    return render(request, 'pages/new_arrivals.html', {'books': books})