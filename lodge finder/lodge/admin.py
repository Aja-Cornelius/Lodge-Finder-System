# lodge/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Lodge, Amenity, LodgeImage


# Optional: Register other models later (e.g., lodges)

@admin.register(Lodge)
class LodgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'owner', 'price_per_year', 'room_type', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'room_type', 'location')
    search_fields = ('name', 'location', 'owner__username')
    list_editable = ('is_approved',)  # ← allows clicking to approve/reject directly
    actions = ['approve_lodges', 'reject_lodges']

    def approve_lodges(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} lodge(s) approved.")
    approve_lodges.short_description = "Approve selected lodges"

    def reject_lodges(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} lodge(s) rejected.")
    reject_lodges.short_description = "Reject selected lodges"

admin.site.register(Amenity)
admin.site.register(LodgeImage)