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
    location = models.CharField(max_length=200, help_text="e.g. Akanu, Ozizza, Backgate, etc.")

    # Distance to FUNAI campus gate
    distance_to_campus = models.CharField(max_length=150, blank=True, default="5 mins walk from Backgate", help_text="e.g. 7 mins walk from Backgate, 5 mins drive from Main Gate")
    
    # Key Highlight Tags (comma separated)
    highlight_tags = models.CharField(max_length=255, blank=True, default="⚡ 24/7 Power, 💧 Borehole Water, 🛡️ Fenced Compound", help_text="Comma-separated highlight tags (e.g. ⚡ 24/7 Power, 💧 Borehole Water, 🛡️ Fenced Compound)")

    # Optional for owner, will be filled by verification agents
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude (filled by verification team)")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude (filled by verification team)")

    price_per_year = models.DecimalField(max_digits=10, decimal_places=2)
    room_type = models.CharField(max_length=50, choices=[
        ('single', 'Single Room'),
        ('self_contain', 'Self-Contain'),
        ('flat', 'Flat'),
    ])
    description = models.TextField(blank=True)
    amenities = models.ManyToManyField('Amenity', blank=True)
    is_approved = models.BooleanField(default=False)

    total_rooms = models.PositiveIntegerField(default=1, help_text="Total number of rooms in the lodge")
    rooms_available = models.PositiveIntegerField(default=1, help_text="Number of rooms currently available")

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def available_percentage(self):
        if self.total_rooms > 0:
            return min(100, int((self.rooms_available / self.total_rooms) * 100))
        return 0

    @property
    def highlight_tag_list(self):
        if self.highlight_tags:
            return [tag.strip() for tag in self.highlight_tags.split(',') if tag.strip()]
        return []

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0.0
        total = sum((r.security_rating + r.water_rating + r.light_rating) / 3.0 for r in reviews)
        return round(total / len(reviews), 1)

    @property
    def rating_count(self):
        return self.reviews.count()

    @property
    def avg_security_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0.0
        return round(sum(r.security_rating for r in reviews) / len(reviews), 1)

    @property
    def avg_water_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0.0
        return round(sum(r.water_rating for r in reviews) / len(reviews), 1)

    @property
    def avg_light_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0.0
        return round(sum(r.light_rating for r in reviews) / len(reviews), 1)

    def __str__(self):
        return f"{self.name} - {self.location}"

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class LodgeImage(models.Model):
    lodge = models.ForeignKey(Lodge, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='lodges/')   # Must be exactly this
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name if self.image else "No image"

class Room(models.Model):
    lodge = models.ForeignKey(Lodge, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100, help_text="e.g. Room 1, Room A, Self-Contain Unit 2")
    description = models.TextField(blank=True, help_text="Describe what's inside the room")
    is_available = models.BooleanField(default=True, help_text="Is this room currently available?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.lodge.name}"

    class Meta:
        ordering = ['created_at']

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name if self.image else "No image"

class Review(models.Model):
    lodge = models.ForeignKey(Lodge, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    security_rating = models.PositiveSmallIntegerField(default=5, help_text="1 to 5 stars for security")
    water_rating = models.PositiveSmallIntegerField(default=5, help_text="1 to 5 stars for water supply")
    light_rating = models.PositiveSmallIntegerField(default=5, help_text="1 to 5 stars for power/light supply")
    comment = models.TextField(blank=True, help_text="Detailed feedback from student")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def overall_rating(self):
        return round((self.security_rating + self.water_rating + self.light_rating) / 3.0, 1)

    def __str__(self):
        return f"Review by {self.user.username} for {self.lodge.name}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    lodge = models.ForeignKey(Lodge, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lodge')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.lodge.name}"