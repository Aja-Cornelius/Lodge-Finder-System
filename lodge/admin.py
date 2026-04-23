from django.contrib import admin
from .models import Lodge, Amenity, LodgeImage

class LodgeImageInline(admin.TabularInline):
    model = LodgeImage
    extra = 3
    max_num = 5


@admin.register(Lodge)
class LodgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'owner', 'price_per_year', 'room_type', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'room_type', 'location')
    search_fields = ('name', 'location', 'owner__username', 'owner__email')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)

    # Better organized form with clear sections
    fieldsets = (
        ('Lodge Information', {
            'fields': ('owner', 'name', 'location', 'room_type', 'price_per_year', 'description', 'amenities')
        }),
        ('Verification - Exact Location', {
            'fields': ('latitude', 'longitude'),
            'description': '<strong>Instructions:</strong><br>'
                           '1. Open Google Maps<br>'
                           '2. Right-click on the exact location of the lodge<br>'
                           '3. Copy the coordinates (first number = Latitude, second = Longitude)<br>'
                           '4. Paste them below.<br><br>'
                           '<em>This will show the precise pin on the map for students.</em>',
            'classes': ('wide',),
        }),
        ('Approval Status', {
            'fields': ('is_approved', 'created_at'),
        }),
    )

    inlines = [LodgeImageInline]

    # Custom actions
    actions = ['approve_lodges', 'reject_lodges']

    def approve_lodges(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} lodge(s) successfully approved.")
    approve_lodges.short_description = "✅ Approve selected lodges"

    def reject_lodges(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} lodge(s) rejected.")
    reject_lodges.short_description = "❌ Reject selected lodges"


admin.site.register(Amenity)
admin.site.register(LodgeImage)