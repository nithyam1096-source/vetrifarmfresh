from django.shortcuts import render
from django.db.models import Count, Avg
from marketplace.models import Product, Category

def home(request):
    featured = Product.objects.filter(availability_status=True, is_featured=True)[:8]
    if featured.count() < 8:
        extra = Product.objects.filter(availability_status=True).exclude(id__in=featured.values_list('id', flat=True))[:8 - featured.count()]
        featured = list(featured) + list(extra)
    new_arrivals = Product.objects.filter(availability_status=True).order_by('-created_at')[:4]
    organic_products = Product.objects.filter(availability_status=True, is_organic=True)[:4]
    categories = Category.objects.annotate(product_count=Count('products')).all()
    return render(request, 'home.html', {
        'featured_products': featured,
        'new_arrivals': new_arrivals,
        'organic_products': organic_products,
        'categories': categories,
    })

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
