from django import forms
from .models import Delivery, DeliveryAgent

class DeliveryStatusForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['delivery_status', 'current_location', 'estimated_delivery_time', 'notes']
        widgets = {
            'estimated_delivery_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DeliveryAgentForm(forms.ModelForm):
    class Meta:
        model = DeliveryAgent
        fields = ['phone', 'address', 'vehicle_type', 'current_location']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
