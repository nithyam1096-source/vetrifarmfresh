from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/farmer/', views.farmer_register, name='farmer_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/customer/', views.customer_profile, name='customer_profile'),
    path('profile/farmer/', views.farmer_profile, name='farmer_profile'),
]
