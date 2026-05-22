from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Delivery, DeliveryAgent
from .forms import DeliveryStatusForm
from marketplace.models import Order

@login_required
def delivery_dashboard(request):
    try:
        agent = DeliveryAgent.objects.get(user=request.user)
    except DeliveryAgent.DoesNotExist:
        messages.error(request, 'Delivery agent profile not found.')
        return redirect('home')

    active_deliveries = Delivery.objects.filter(delivery_agent=agent).exclude(delivery_status='delivered').exclude(delivery_status='failed')
    completed_deliveries = Delivery.objects.filter(delivery_agent=agent, delivery_status='delivered')[:10]

    context = {
        'agent': agent,
        'active_deliveries': active_deliveries,
        'completed_deliveries': completed_deliveries,
        'active_count': active_deliveries.count(),
        'completed_count': completed_deliveries.count(),
    }
    return render(request, 'delivery/dashboard.html', context)

@login_required
def assigned_deliveries(request):
    try:
        agent = DeliveryAgent.objects.get(user=request.user)
    except DeliveryAgent.DoesNotExist:
        messages.error(request, 'Delivery agent profile not found.')
        return redirect('home')

    deliveries = Delivery.objects.filter(delivery_agent=agent).order_by('-created_at')
    return render(request, 'delivery/assigned_deliveries.html', {'deliveries': deliveries})

@login_required
def update_delivery_status(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    if delivery.delivery_agent.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('delivery:dashboard')

    if request.method == 'POST':
        form = DeliveryStatusForm(request.POST, instance=delivery)
        if form.is_valid():
            delivery = form.save(commit=False)
            if delivery.delivery_status == 'delivered':
                from django.utils import timezone
                delivery.delivered_at = timezone.now()
                delivery.order.order_status = 'delivered'
                delivery.order.save()
            delivery.save()
            messages.success(request, f'Delivery #{delivery.id} status updated to {delivery.get_delivery_status_display()}.')
            return redirect('delivery:assigned_deliveries')
    else:
        form = DeliveryStatusForm(instance=delivery)
    return render(request, 'delivery/update_status.html', {'form': form, 'delivery': delivery})

@login_required
def delivery_detail(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    return render(request, 'delivery/delivery_detail.html', {'delivery': delivery})
