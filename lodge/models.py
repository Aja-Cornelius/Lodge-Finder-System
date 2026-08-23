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
    
    # Transport & Commute Estimator
    keke_fare = models.CharField(max_length=150, blank=True, default="₦100 Keke fare to Main Gate", help_text="e.g. ₦100 Keke fare to Main Gate or 🚶 5 mins walk")

    # Key Highlight Tags (comma separated)
    highlight_tags = models.CharField(max_length=255, blank=True, default="⚡ 24/7 Power, 💧 Borehole Water, 🛡️ Fenced Compound", help_text="Comma-separated highlight tags (e.g. ⚡ 24/7 Power, 💧 Borehole Water, 🛡️ Fenced Compound)")

    # Upfront Fees Breakdown
    price_per_year = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base rent per year")
    agreement_fee = models.DecimalField(max_digits=10, decimal_places=2, default=15000, help_text="Agreement & Legal commission fee")
    caution_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10000, help_text="Refundable caution deposit")
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=5000, help_text="Annual service charge (cleaning, waste)")

    # Physical Inspection & Verification Scorecard
    is_physically_inspected = models.BooleanField(default=True, help_text="Physically inspected by LodgeFinder team")
    inspection_score = models.PositiveSmallIntegerField(default=95, help_text="Overall inspection score (0 to 100)")
    inspection_report_notes = models.TextField(blank=True, default="Inspected by LodgeFinder Agents. Verified road access, functioning borehole, secure compound gate, and good light transformer supply.", help_text="Official inspection summary notes")

    # Optional for owner, will be filled by verification agents
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude (filled by verification team)")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude (filled by verification team)")

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
    def total_upfront_cost(self):
        return self.price_per_year + self.agreement_fee + self.caution_fee + self.service_charge

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

class RoommatePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roommate_posts')
    title = models.CharField(max_length=200, help_text="e.g. Looking for 200L Male Roommate at Backgate")
    lodge = models.ForeignKey(Lodge, on_delete=models.SET_NULL, null=True, blank=True, related_name='roommate_requests', help_text="Optional link to specific lodge")
    location_preference = models.CharField(max_length=150, help_text="e.g. Backgate, Ozizza, Frontgate")
    budget_per_year = models.DecimalField(max_digits=10, decimal_places=2, help_text="Budget contribution (e.g. 100000)")
    gender_preference = models.CharField(max_length=20, choices=[('male', 'Male Only'), ('female', 'Female Only'), ('any', 'Any Gender')], default='any')
    department_level = models.CharField(max_length=100, help_text="e.g. Computer Science, 300 Level")
    contact_phone = models.CharField(max_length=15, help_text="Phone/WhatsApp number for interested roommates")
    notes = models.TextField(blank=True, help_text="Habits, rules, study preferences, etc.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

class AlertSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_subscriptions')
    location = models.CharField(max_length=100, blank=True, help_text="Location keyword (e.g. Backgate)")
    room_type = models.CharField(max_length=50, blank=True, choices=[('', 'Any Room Type'), ('single', 'Single Room'), ('self_contain', 'Self-Contain'), ('flat', 'Flat')])
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum budget")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert for {self.user.username} - {self.location or 'All Areas'}"