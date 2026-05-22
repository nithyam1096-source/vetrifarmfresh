from django.urls import path
from . import admin_views

urlpatterns = [
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    path('customers/', admin_views.admin_customers, name='admin_customers'),
    path('farmers/', admin_views.admin_farmers, name='admin_farmers'),
    path('farmers/approve/<int:farmer_id>/', admin_views.admin_approve_farmer, name='admin_approve_farmer'),
    path('users/block/<int:user_id>/', admin_views.admin_block_user, name='admin_block_user'),
    path('products/', admin_views.admin_products, name='admin_products'),
    path('categories/', admin_views.admin_categories, name='admin_categories'),
    path('categories/add/', admin_views.admin_add_category, name='admin_add_category'),
    path('orders/', admin_views.admin_orders, name='admin_orders'),
    path('inventory/', admin_views.admin_inventory, name='admin_inventory'),
    path('reports/', admin_views.admin_reports, name='admin_reports'),
    path('deliveries/', admin_views.admin_deliveries, name='admin_deliveries'),
]
