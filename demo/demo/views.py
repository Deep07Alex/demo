from django.http import HttpResponse
from django.shortcuts import render

def home_page(request):
    return render(request, 'index.html')


def Aboutus(request):
    return render(request, 'pages/Aboutus.html')

def contact_information(request):
    return render(request, 'pages/contactinformation.html')

