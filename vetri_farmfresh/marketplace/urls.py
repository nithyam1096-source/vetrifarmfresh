from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment_simulation, name='payment_simulation'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.my_orders, name='my_orders'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
]
