from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Lodge, Amenity
from .forms import LodgeForm

User = get_user_model()

class LodgeModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123', user_type='owner')

    def test_available_percentage(self):
        lodge = Lodge.objects.create(
            owner=self.owner,
            name="Test Lodge",
            location="Akanu",
            price_per_year=150000.00,
            room_type="single",
            total_rooms=10,
            rooms_available=3
        )
        self.assertEqual(lodge.available_percentage, 30)

        lodge.rooms_available = 0
        self.assertEqual(lodge.available_percentage, 0)

        # Edge case: total_rooms is 0
        lodge.total_rooms = 0
        self.assertEqual(lodge.available_percentage, 0)

class LodgeFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123', user_type='owner')
        self.amenity, _ = Amenity.objects.get_or_create(name="Running Water")

    def test_valid_lodge_form(self):
        form_data = {
            'name': 'Nazareth Lodge',
            'location': 'Backgate',
            'price_per_year': 200000.00,
            'room_type': 'single',
            'description': 'Nice lodge',
            'amenities': [self.amenity.id],
            'total_rooms': 8,
            'rooms_available': 2,
        }
        form = LodgeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_rooms_available_form(self):
        form_data = {
            'name': 'Nazareth Lodge',
            'location': 'Backgate',
            'price_per_year': 200000.00,
            'room_type': 'single',
            'description': 'Nice lodge',
            'amenities': [self.amenity.id],
            'total_rooms': 5,
            'rooms_available': 6, # More available than total
        }
        form = LodgeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rooms_available', form.errors)
        self.assertEqual(form.errors['rooms_available'][0], 'Rooms available cannot be greater than the total number of rooms.')
