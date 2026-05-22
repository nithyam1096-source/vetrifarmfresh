from django.urls import path
from . import views

app_name = 'farmer'

urlpatterns = [
    path('dashboard/', views.farmer_dashboard, name='dashboard'),
    path('products/add/', views.farmer_add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.farmer_edit_product, name='edit_product'),
    path('inventory/', views.farmer_inventory, name='inventory'),
    path('orders/', views.farmer_orders, name='orders'),
    path('orders/update/<int:order_id>/', views.farmer_update_order_status, name='update_order_status'),
    path('sales-report/', views.farmer_sales_report, name='sales_report'),
]
