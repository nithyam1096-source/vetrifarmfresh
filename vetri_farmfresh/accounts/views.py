from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomerRegistrationForm, FarmerRegistrationForm, CustomerProfileForm, FarmerProfileForm, UserUpdateForm
from .models import Customer, Farmer
from django.contrib.auth.models import User
from django.db import transaction

def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to FarmFresh.')
            return redirect('home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/customer_register.html', {'form': form})

def farmer_register(request):
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Farmer registration successful! Your account is pending approval.')
            return redirect('home')
    else:
        form = FarmerRegistrationForm()
    return render(request, 'accounts/farmer_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not hasattr(user, 'customer') and not hasattr(user, 'farmer') and not user.is_staff:
                Customer.objects.get_or_create(user=user, defaults={'phone': '', 'address': ''})
            if not hasattr(user, 'customer') and not hasattr(user, 'farmer') and user.is_staff:
                Customer.objects.get_or_create(user=user, defaults={'phone': '', 'address': ''})
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def customer_profile(request):
    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={'phone': '', 'address': ''})

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:customer_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=customer)
    return render(request, 'accounts/customer_profile.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def farmer_profile(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        messages.error(request, 'Farmer profile not found.')
        return redirect('home')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:farmer_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = FarmerProfileForm(instance=farmer)
    return render(request, 'accounts/farmer_profile.html', {'user_form': user_form, 'profile_form': profile_form})
