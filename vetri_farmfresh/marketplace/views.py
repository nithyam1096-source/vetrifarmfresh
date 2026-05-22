from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, Cart, Order, OrderItem, Wishlist, Review
from .forms import ProductForm, ReviewForm
from accounts.models import Customer, Farmer
from datetime import date

def product_list(request):
    products = Product.objects.filter(availability_status=True)
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('search')
    organic_only = request.GET.get('organic')

    if selected_category:
        products = products.filter(category_id=selected_category)

    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    if organic_only:
        products = products.filter(is_organic=True)

    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'latest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'sort_by': sort_by,
        'search_query': search_query,
        'organic_only': organic_only,
    }
    return render(request, 'marketplace/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    related_products = Product.objects.filter(category=product.category, availability_status=True).exclude(id=product_id)[:4]

    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            in_wishlist = Wishlist.objects.filter(customer=customer, product=product).exists()
            existing_review = Review.objects.filter(customer=customer, product=product).first()
        except Customer.DoesNotExist:
            in_wishlist = False
            existing_review = None
    else:
        in_wishlist = False
        existing_review = None

    if request.method == 'POST' and request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            form = ReviewForm(request.POST, instance=existing_review)
            if form.is_valid():
                review = form.save(commit=False)
                review.customer = customer
                review.product = product
                review.save()
                messages.success(request, 'Review submitted successfully!')
                return redirect('marketplace:product_detail', product_id=product.id)
        except Customer.DoesNotExist:
            messages.error(request, 'Only customers can submit reviews.')

    form = ReviewForm(instance=existing_review)

    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'form': form,
    }
    return render(request, 'marketplace/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer, created = Customer.objects.get_or_create(user=request.user, defaults={'phone': '', 'address': ''})
    if created:
        messages.info(request, 'A customer profile has been created for your account.')

    cart_item, created = Cart.objects.get_or_create(customer=customer, product=product)
    if not created:
        if cart_item.quantity < product.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Increased {product.name} quantity in cart.')
        else:
            messages.warning(request, 'Stock limit reached.')
    else:
        messages.success(request, f'{product.name} added to cart.')
    return redirect('marketplace:view_cart')

@login_required
def view_cart(request):
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'phone': '', 'address': ''})
    cart_items = Cart.objects.filter(customer=customer)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'marketplace/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= cart_item.product.stock_quantity:
            cart_item.quantity = quantity
            cart_item.save()
        elif quantity > cart_item.product.stock_quantity:
            messages.warning(request, 'Not enough stock available.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
    return redirect('marketplace:view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('marketplace:view_cart')

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'phone': '', 'address': ''})
    wishlist_item, created = Wishlist.objects.get_or_create(customer=customer, product=product)
    if created:
        messages.success(request, f'{product.name} added to wishlist.')
    else:
        wishlist_item.delete()
        messages.success(request, f'{product.name} removed from wishlist.')
    return redirect('marketplace:product_detail', product_id=product_id)

@login_required
def view_wishlist(request):
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'phone': '', 'address': ''})
    wishlist_items = Wishlist.objects.filter(customer=customer)
    return render(request, 'marketplace/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def checkout(request):
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'phone': '', 'address': ''})
    cart_items = Cart.objects.filter(customer=customer)
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('marketplace:view_cart')

    total = sum(item.total_price() for item in cart_items)

    SLOTS = [
        '6 AM - 8 AM',
        '9 AM - 12 PM',
        '1 PM - 4 PM',
        '5 PM - 8 PM',
    ]

    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', customer.address)
        delivery_slot = request.POST.get('delivery_slot')
        payment_method = request.POST.get('payment_method', 'cod')

        if not delivery_slot:
            messages.error(request, 'Please select a delivery slot.')
            return render(request, 'marketplace/checkout.html', {
                'cart_items': cart_items, 'total': total, 'slots': SLOTS, 'customer': customer
            })

        order = Order.objects.create(
            customer=customer,
            delivery_address=delivery_address,
            delivery_slot=delivery_slot,
            total_amount=total,
            payment_method=payment_method,
            payment_status='pending' if payment_method == 'cod' else 'completed',
            transaction_id='',
        )

        if payment_method == 'online':
            order.transaction_id = f'TXN{order.id}{customer.id}{int(date.today().strftime("%Y%m%d%H%M%S"))}'
            order.save()

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            )
            product = item.product
            product.stock_quantity -= item.quantity
            if product.stock_quantity <= 0:
                product.availability_status = False
            product.save()

        cart_items.delete()

        if payment_method == 'online':
            return redirect('marketplace:payment_simulation', order_id=order.id)

        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('marketplace:order_confirmation', order_id=order.id)

    return render(request, 'marketplace/checkout.html', {
        'cart_items': cart_items, 'total': total, 'slots': SLOTS, 'customer': customer
    })

@login_required
def payment_simulation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.payment_status = 'completed'
        order.transaction_id = f'TXN{order.id}{order.customer.user.id}{int(date.today().strftime("%Y%m%d%H%M%S"))}'
        order.save()
        messages.success(request, f'Payment successful! Order #{order.id} confirmed.')
        return redirect('marketplace:order_confirmation', order_id=order.id)
    return render(request, 'marketplace/payment.html', {'order': order})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    return render(request, 'marketplace/order_confirmation.html', {'order': order})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.customer.user != request.user and not request.user.is_staff:
        try:
            farmer = Farmer.objects.get(user=request.user)
        except Farmer.DoesNotExist:
            messages.error(request, 'Access denied.')
            return redirect('home')
    return render(request, 'marketplace/order_detail.html', {'order': order})

@login_required
def my_orders(request):
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'phone': '', 'address': ''})
    orders = Order.objects.filter(customer=customer).order_by('-ordered_date')
    return render(request, 'marketplace/my_orders.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.order_status in ['pending', 'confirmed']:
        order.order_status = 'cancelled'
        order.save()
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.availability_status = True
                item.product.save()
        messages.success(request, f'Order #{order.id} cancelled.')
    else:
        messages.error(request, 'Order cannot be cancelled at this stage.')
    return redirect('marketplace:my_orders')

@login_required
def download_invoice(request, order_id):
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    import html.parser

    order = get_object_or_404(Order, id=order_id)
    if order.customer.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')

    html_string = render_to_string('marketplace/invoice.html', {'order': order})
    response = HttpResponse(html_string, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.html"'
    return response

# Farmer views

@login_required
def farmer_dashboard(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer profile required.')
        return redirect('home')

    products = Product.objects.filter(farmer=farmer)
    total_products = products.count()
    low_stock = products.filter(stock_quantity__lt=10).count()
    out_of_stock = products.filter(availability_status=False).count()
    orders = OrderItem.objects.filter(product__farmer=farmer).select_related('order', 'product')

    context = {
        'farmer': farmer,
        'total_products': total_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'orders': orders,
        'products': products,
    }
    return render(request, 'farmer/dashboard.html', context)

@login_required
def farmer_add_product(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer profile required.')
        return redirect('home')

    if not farmer.is_approved:
        messages.warning(request, 'Your account is pending approval.')
        return redirect('farmer:dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = farmer
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('farmer:inventory')
    else:
        form = ProductForm()
    return render(request, 'farmer/add_product.html', {'form': form})

@login_required
def farmer_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.farmer.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('farmer:dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('farmer:inventory')
    else:
        form = ProductForm(instance=product)
    return render(request, 'farmer/edit_product.html', {'form': form, 'product': product})

@login_required
def farmer_inventory(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer profile required.')
        return redirect('home')

    products = Product.objects.filter(farmer=farmer).order_by('-created_at')
    low_stock_products = products.filter(stock_quantity__lt=10)
    return render(request, 'farmer/inventory.html', {'products': products, 'low_stock_products': low_stock_products})

@login_required
def farmer_orders(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer profile required.')
        return redirect('home')

    order_items = OrderItem.objects.filter(product__farmer=farmer).select_related('order', 'product').order_by('-order__ordered_date')
    orders_dict = {}
    for item in order_items:
        if item.order.id not in orders_dict:
            orders_dict[item.order.id] = {'order': item.order, 'items': []}
        orders_dict[item.order.id]['items'].append(item)

    return render(request, 'farmer/orders.html', {'orders_dict': orders_dict})

@login_required
def farmer_update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('order_status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.order_status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}.')
    return redirect('farmer:orders')

@login_required
def farmer_sales_report(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer profile required.')
        return redirect('home')

    order_items = OrderItem.objects.filter(product__farmer=farmer, order__order_status='delivered')
    total_sales = sum(item.price * item.quantity for item in order_items)
    total_orders = order_items.values('order').distinct().count()
    products = Product.objects.filter(farmer=farmer)

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'order_items': order_items,
        'products': products,
    }
    return render(request, 'farmer/sales_report.html', context)
