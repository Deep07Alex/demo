# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Book

def home_page(request):
    books = Book.objects.all().order_by('title')
    return render(request, 'index.html', {'books': books})

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    return render(request, 'book_detail.html', {'book': book})