# lodge/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Lodge, Amenity, LodgeImage

class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        if commit:
            user.save()
        return user

class OwnerSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'owner'
        if commit:
            user.save()
        return user

class LodgeForm(forms.ModelForm):
    class Meta:
        model = Lodge
        fields = ['name', 'location', 'price_per_year', 'room_type', 'description', 'amenities']
        widgets = {
            'amenities': forms.CheckboxSelectMultiple(),
        }

class LodgeImageForm(forms.ModelForm):
    class Meta:
        model = LodgeImage
        fields = ['image']