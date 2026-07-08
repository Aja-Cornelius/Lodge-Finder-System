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
        fields = ['name', 'location', 'price_per_year', 'room_type', 'description', 'amenities', 'total_rooms', 'rooms_available']
        # Note: latitude and longitude are NOT included → owner cannot see them
        widgets = {
            'amenities': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        total_rooms = cleaned_data.get('total_rooms')
        rooms_available = cleaned_data.get('rooms_available')

        if total_rooms is not None and rooms_available is not None:
            if rooms_available > total_rooms:
                self.add_error('rooms_available', 'Rooms available cannot be greater than the total number of rooms.')
        return cleaned_data

class LodgeImageForm(forms.ModelForm):
    class Meta:
        model = LodgeImage
        fields = ['image']