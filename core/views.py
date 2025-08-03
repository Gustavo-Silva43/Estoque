from django.shortcuts import render
from django.http import HttpResponse 

def index(request):
    return render(request, 'index.html') 

def product_list(request):
    return render(request, 'core/product_list.html', {}) 
