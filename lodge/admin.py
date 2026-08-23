from django.contrib import admin
from .models import Lodge, Amenity, LodgeImage, Room, RoomImage, Review, Favorite

class LodgeImageInline(admin.TabularInline):
    model = LodgeImage
    extra = 3
    max_num = 9

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3
    max_num = 6

class RoomInline(admin.StackedInline):
    model = Room
    extra = 0
    show_change_link = True
    fields = ('name', 'description', 'is_available')


@admin.register(Lodge)
class LodgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'distance_to_campus', 'owner', 'price_per_year', 'room_type', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'room_type', 'location')
    search_fields = ('name', 'location', 'owner__username', 'owner__email', 'distance_to_campus')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)

    # Better organized form with clear sections
    fieldsets = (
        ('Lodge Information', {
            'fields': ('owner', 'name', 'location', 'distance_to_campus', 'highlight_tags', 'room_type', 'price_per_year', 'description', 'amenities')
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

    inlines = [LodgeImageInline, RoomInline]

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


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'lodge', 'is_available', 'created_at')
    list_filter = ('is_available', 'lodge')
    search_fields = ('name', 'lodge__name')
    list_editable = ('is_available',)
    inlines = [RoomImageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('lodge', 'user', 'overall_rating', 'security_rating', 'water_rating', 'light_rating', 'created_at')
    list_filter = ('security_rating', 'water_rating', 'light_rating')
    search_fields = ('lodge__name', 'user__username', 'comment')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'lodge', 'created_at')
    search_fields = ('user__username', 'lodge__name')


admin.site.register(Amenity)
admin.site.register(LodgeImage)
admin.site.register(RoomImage)