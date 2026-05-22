from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator
from accounts.models import Customer, Farmer
from marketplace.models import Product, Category, Order, OrderItem, Review
from delivery.models import Delivery, DeliveryAgent
from django.contrib.auth.models import User

@staff_member_required
def admin_dashboard(request):
    total_customers = Customer.objects.count()
    total_farmers = Farmer.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status='pending').count()
    total_revenue = Order.objects.filter(order_status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    low_stock_products = Product.objects.filter(stock_quantity__lt=10).count()
    recent_orders = Order.objects.order_by('-ordered_date')[:5]
    recent_products = Product.objects.order_by('-created_at')[:5]

    context = {
        'total_customers': total_customers,
        'total_farmers': total_farmers,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@staff_member_required
def admin_customers(request):
    customers = Customer.objects.select_related('user').all()
    return render(request, 'admin_panel/customers.html', {'customers': customers})

@staff_member_required
def admin_farmers(request):
    farmers = Farmer.objects.select_related('user').all()
    return render(request, 'admin_panel/farmers.html', {'farmers': farmers})

@staff_member_required
def admin_approve_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    farmer.is_approved = not farmer.is_approved
    farmer.save()
    status = 'approved' if farmer.is_approved else 'disapproved'
    messages.success(request, f'Farmer {farmer.farm_name} {status}.')
    return redirect('admin_farmers')

@staff_member_required
def admin_block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = 'blocked' if not user.is_active else 'unblocked'
    messages.success(request, f'User {user.username} {status}.')
    return redirect('admin_customers')

@staff_member_required
def admin_products(request):
    products = Product.objects.select_related('farmer', 'category').all()
    return render(request, 'admin_panel/products.html', {'products': products})

@staff_member_required
def admin_categories(request):
    CATEGORY_NAMES = [
        'Vegetables', 'Fruits', 'Organic Products', 'Dairy',
        'Grains', 'Seeds', 'Herbs', 'Spices',
        'Nuts & Dry Fruits', 'Beverages', 'Honey & Jaggery', 'Oils & Ghee',
        'Fertilizers', 'Farming Tools', 'Flowers', 'Meat & Eggs',
    ]
    for name in CATEGORY_NAMES:
        Category.objects.get_or_create(name=name)

    CATEGORY_ICONS = {
        'Vegetables': 'fa-carrot',
        'Fruits': 'fa-apple-whole',
        'Organic Products': 'fa-leaf',
        'Dairy': 'fa-cheese',
        'Grains': 'fa-wheat-awn',
        'Seeds': 'fa-seedling',
        'Herbs': 'fa-spa',
        'Spices': 'fa-mortar-pestle',
        'Nuts & Dry Fruits': 'fa-bag-shopping',
        'Beverages': 'fa-mug-hot',
        'Honey & Jaggery': 'fa-jar',
        'Oils & Ghee': 'fa-oil-can',
        'Fertilizers': 'fa-flask',
        'Farming Tools': 'fa-tractor',
        'Flowers': 'fa-flower',
        'Meat & Eggs': 'fa-drumstick-bite',
    }

    categories = Category.objects.annotate(product_count=Count('products')).all()
    for cat in categories:
        cat.icon = CATEGORY_ICONS.get(cat.name, 'fa-tag')
    return render(request, 'admin_panel/categories.html', {'categories': categories})

@staff_member_required
def admin_add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        if name:
            Category.objects.create(name=name, image=image)
            messages.success(request, 'Category added successfully.')
            return redirect('admin_categories')
    return render(request, 'admin_panel/add_category.html')

@staff_member_required
def admin_orders(request):
    orders = Order.objects.select_related('customer__user').all().order_by('-ordered_date')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    return render(request, 'admin_panel/orders.html', {'orders': orders})

@staff_member_required
def admin_inventory(request):
    products = Product.objects.select_related('farmer', 'category').all().order_by('stock_quantity')
    low_stock = products.filter(stock_quantity__lt=10)
    out_of_stock = products.filter(availability_status=False)
    return render(request, 'admin_panel/inventory.html', {
        'products': products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    })

@staff_member_required
def admin_reports(request):
    total_revenue = Order.objects.filter(order_status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()
    total_farmers = Farmer.objects.filter(is_approved=True).count()
    category_stats = Category.objects.annotate(product_count=Count('products'))
    monthly_orders = Order.objects.extra(month="strftime('%%m', ordered_date)").values('month').annotate(count=Count('id'))

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_farmers': total_farmers,
        'category_stats': category_stats,
    }
    return render(request, 'admin_panel/reports.html', context)

@staff_member_required
def admin_deliveries(request):
    deliveries = Delivery.objects.select_related('order', 'delivery_agent__user').all()
    return render(request, 'admin_panel/deliveries.html', {'deliveries': deliveries})
