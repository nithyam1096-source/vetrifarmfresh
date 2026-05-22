from django.contrib import admin
from .models import Delivery, DeliveryAgent

@admin.register(DeliveryAgent)
class DeliveryAgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'vehicle_type', 'is_available']
    list_filter = ['is_available', 'vehicle_type']
    search_fields = ['user__username', 'phone']

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'delivery_agent', 'delivery_status', 'estimated_delivery_time', 'created_at']
    list_filter = ['delivery_status']
    search_fields = ['order__id', 'delivery_agent__user__username']
