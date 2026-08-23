# lodge/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Lodge, Amenity, LodgeImage, Room, RoomImage, Review, Favorite

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
        fields = ['name', 'location', 'distance_to_campus', 'highlight_tags', 'price_per_year', 'room_type', 'description', 'amenities', 'total_rooms', 'rooms_available']
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

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'description', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class RoomImageForm(forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = ['image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['security_rating', 'water_rating', 'light_rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your experience living at or inspecting this lodge...'}),
        }