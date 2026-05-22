import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmfresh.settings')
sys.path.insert(0, os.path.dirname(__file__))
import django
django.setup()
from django.conf import settings
from marketplace.models import Category, Product

for cat_id, cat_name in [(15, 'Flowers'), (16, 'Meat & Eggs')]:
    cat = Category.objects.get(id=cat_id)
    p_count = Product.objects.filter(category=cat).count()
    Product.objects.filter(category=cat).delete()
    cat.delete()
    print(f'Deleted "{cat_name}" with {p_count} products')
