from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Order

class DeliveryAgent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    vehicle_type = models.CharField(max_length=100, blank=True)
    is_available = models.BooleanField(default=True)
    current_location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Delivery(models.Model):
    DELIVERY_STATUS = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    delivery_agent = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL, null=True, related_name='deliveries')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='assigned')
    current_location = models.CharField(max_length=255, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery #{self.id} - Order #{self.order.id}"

    class Meta:
        verbose_name_plural = 'Deliveries'
