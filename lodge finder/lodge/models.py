# lodge/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('owner', 'Lodge Owner'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # NEW FIELD:
    full_name = models.CharField(max_length=150, blank=True, help_text="Full name (e.g., Cornelius Okoro)")

    def __str__(self):
        return self.username

User = get_user_model()

class Lodge(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lodges')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, help_text="e.g. Akanu / Campus Gate")
    price_per_year = models.DecimalField(max_digits=10, decimal_places=2)
    room_type = models.CharField(max_length=50, choices=[
        ('single', 'Single Room'),
        ('self_contain', 'Self-Contain'),
        ('flat', 'Flat'),
    ])
    description = models.TextField(blank=True)
    amenities = models.ManyToManyField('Amenity', blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class LodgeImage(models.Model):
    lodge = models.ForeignKey(Lodge, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='lodges/')
    uploaded_at = models.DateTimeField(auto_now_add=True)