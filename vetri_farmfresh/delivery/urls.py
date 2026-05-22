from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('dashboard/', views.delivery_dashboard, name='dashboard'),
    path('assigned/', views.assigned_deliveries, name='assigned_deliveries'),
    path('update/<int:delivery_id>/', views.update_delivery_status, name='update_status'),
    path('<int:delivery_id>/', views.delivery_detail, name='delivery_detail'),
]
