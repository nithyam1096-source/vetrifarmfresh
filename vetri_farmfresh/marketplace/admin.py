from django.contrib import admin
from .models import Category, Product, Cart, Order, OrderItem, Wishlist, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    prepopulated_fields = {'name': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer', 'category', 'price', 'stock_quantity', 'is_organic', 'is_featured', 'availability_status']
    list_filter = ['category', 'is_organic', 'is_featured', 'availability_status']
    search_fields = ['name', 'farmer__farm_name']
    list_editable = ['is_featured', 'availability_status']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_amount', 'order_status', 'payment_status', 'ordered_date']
    list_filter = ['order_status', 'payment_status']
    search_fields = ['customer__user__username']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'rating', 'created_at']
