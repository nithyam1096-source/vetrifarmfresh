from django.contrib import admin
from .models import Customer, Farmer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ['farm_name', 'user', 'contact_number', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    search_fields = ['farm_name', 'user__username']
    actions = ['approve_farmers']

    def approve_farmers(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} farmers approved.')
    approve_farmers.short_description = 'Approve selected farmers'
