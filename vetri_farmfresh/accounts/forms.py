from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Farmer

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address']
            )
        return user

class FarmerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    farm_name = forms.CharField(max_length=200, required=True)
    farm_address = forms.CharField(widget=forms.Textarea, required=True)
    contact_number = forms.CharField(max_length=15, required=True)
    farm_description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Farmer.objects.create(
                user=user,
                farm_name=self.cleaned_data['farm_name'],
                farm_address=self.cleaned_data['farm_address'],
                contact_number=self.cleaned_data['contact_number'],
                farm_description=self.cleaned_data.get('farm_description', '')
            )
        return user

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['farm_name', 'farm_address', 'contact_number', 'farm_description', 'profile_image']
        widgets = {
            'farm_address': forms.Textarea(attrs={'rows': 3}),
            'farm_description': forms.Textarea(attrs={'rows': 4}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
