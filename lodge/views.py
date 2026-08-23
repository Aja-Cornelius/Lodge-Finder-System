# lodge/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.db.models import Q
from django.forms import formset_factory

from .forms import StudentSignUpForm, OwnerSignUpForm, LodgeForm, LodgeImageForm, RoomForm, RoomImageForm, ReviewForm
from .models import Lodge, Amenity, LodgeImage, Room, RoomImage, Review, Favorite


def home(request):
    # Fetch the 9 most recent approved lodges for the landing page
    recent_lodges = Lodge.objects.filter(is_approved=True)\
                         .prefetch_related('images', 'amenities', 'reviews')\
                         .select_related('owner')\
                         .order_by('-created_at')[:9]

    favorited_lodge_ids = set()
    if request.user.is_authenticated and request.user.user_type == 'student':
        favorited_lodge_ids = set(Favorite.objects.filter(user=request.user).values_list('lodge_id', flat=True))

    return render(request, 'lodge/landing.html', {
        'recent_lodges': recent_lodges,
        'favorited_lodge_ids': favorited_lodge_ids,
    })

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('student_dashboard')
    else:
        form = StudentSignUpForm()
    return render(request, 'lodge/student_signup.html', {'form': form})

def owner_signup(request):
    if request.method == 'POST':
        form = OwnerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('owner_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OwnerSignUpForm()
    return render(request, 'lodge/owner_signup.html', {'form': form})

def student_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)
        if user is not None:
            if user.user_type == 'student':
                login(request, user)
                messages.success(request, 'Login successful! Welcome back.')
                return redirect('student_dashboard')
            else:
                messages.error(request, 'This account is not a student account.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    return render(request, 'lodge/student_login.html')

def owner_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)
        if user is not None:
            if user.user_type == 'owner':
                login(request, user)
                messages.success(request, 'Login successful! Welcome back.')
                return redirect('owner_dashboard')
            else:
                messages.error(request, 'This account is not a lodge owner account.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    return render(request, 'lodge/owner_login.html')

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        messages.error(request, 'You do not have access to this page.')
        return redirect('home')

    approved_lodges = Lodge.objects.filter(is_approved=True)

    total_lodges = approved_lodges.count()
    total_locations = approved_lodges.values('location').distinct().count()
    total_room_types = approved_lodges.values('room_type').distinct().count()

    # Fetch 9 recommended approved lodges
    recommended_lodges = approved_lodges\
                              .prefetch_related('images', 'amenities', 'reviews')\
                              .select_related('owner')\
                              .order_by('-created_at')[:9]

    # Saved lodges (Wishlist)
    saved_favorites = Favorite.objects.filter(user=request.user).select_related('lodge').prefetch_related('lodge__images', 'lodge__reviews')
    saved_lodges = [fav.lodge for fav in saved_favorites]
    favorited_lodge_ids = set(fav.lodge_id for fav in saved_favorites)

    return render(request, 'lodge/student_dashboard.html', {
        'recommended_lodges': recommended_lodges,
        'saved_lodges': saved_lodges,
        'favorited_lodge_ids': favorited_lodge_ids,
        'total_lodges': total_lodges,
        'total_locations': total_locations,
        'total_room_types': total_room_types,
    })

@login_required
def owner_dashboard(request):
    if request.user.user_type != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')

    my_lodges = Lodge.objects.filter(owner=request.user)\
                             .select_related('owner')\
                             .prefetch_related('images', 'amenities')\
                             .order_by('-created_at')

    total_lodges = my_lodges.count()
    approved = my_lodges.filter(is_approved=True).count()
    pending = my_lodges.filter(is_approved=False).count()

    return render(request, 'lodge/owner_dashboard.html', {
        'my_lodges': my_lodges,
        'total_lodges': total_lodges,
        'approved': approved,
        'pending': pending,
    })

@login_required
def add_lodge(request):
    if request.user.user_type != 'owner':
        messages.error(request, 'Only lodge owners can add lodges.')
        return redirect('home')

    ImageFormSet = formset_factory(LodgeImageForm, extra=9)  # Up to 9 photos

    if request.method == 'POST':
        form = LodgeForm(request.POST)
        image_formset = ImageFormSet(request.POST, request.FILES)

        if form.is_valid() and image_formset.is_valid():
            lodge = form.save(commit=False)
            lodge.owner = request.user
            lodge.save()
            form.save_m2m()

            for image_form in image_formset:
                if image_form.cleaned_data.get('image'):
                    LodgeImage.objects.create(lodge=lodge, image=image_form.cleaned_data['image'])

            messages.success(request, 'Lodge registered successfully! Waiting for admin approval.')
            return redirect('owner_dashboard')
    else:
        form = LodgeForm()
        image_formset = ImageFormSet()

    return render(request, 'lodge/add_lodge.html', {
        'form': form,
        'image_formset': image_formset,
    })

def search_results(request):
    lodges = Lodge.objects.filter(is_approved=True)\
                          .select_related('owner')\
                          .prefetch_related('images', 'amenities', 'reviews')\
                          .order_by('-created_at')

    location = request.GET.get('location')
    room_type = request.GET.get('room_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if location:
        lodges = lodges.filter(Q(location__icontains=location) | Q(name__icontains=location) | Q(distance_to_campus__icontains=location))
    if room_type:
        lodges = lodges.filter(room_type=room_type)
    if min_price:
        try:
            lodges = lodges.filter(price_per_year__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            lodges = lodges.filter(price_per_year__lte=float(max_price))
        except (ValueError, TypeError):
            pass

    total_results = lodges.count()
    paginator = Paginator(lodges, 9) # 9 lodges per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    favorited_lodge_ids = set()
    if request.user.is_authenticated and request.user.user_type == 'student':
        favorited_lodge_ids = set(Favorite.objects.filter(user=request.user).values_list('lodge_id', flat=True))

    return render(request, 'lodge/search_results.html', {
        'page_obj': page_obj,
        'total_results': total_results,
        'filters': request.GET,
        'favorited_lodge_ids': favorited_lodge_ids,
    })

def lodge_detail(request, lodge_id):
    lodge = get_object_or_404(Lodge, id=lodge_id)

    if not lodge.is_approved and lodge.owner != request.user:
        raise Http404("This lodge is not yet approved.")

    images = lodge.images.all()
    rooms = lodge.rooms.prefetch_related('images').all()
    reviews = lodge.reviews.select_related('user').all()

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, lodge=lodge).exists()

    review_form = ReviewForm()

    # Similar lodges in location
    related_lodges = Lodge.objects.filter(is_approved=True, location=lodge.location)\
                                  .exclude(id=lodge.id)\
                                  .prefetch_related('images', 'reviews')[:3]

    return render(request, 'lodge/lodge_detail.html', {
        'lodge': lodge,
        'images': images,
        'rooms': rooms,
        'reviews': reviews,
        'is_favorited': is_favorited,
        'review_form': review_form,
        'related_lodges': related_lodges,
    })

@login_required
def add_review(request, lodge_id):
    lodge = get_object_or_404(Lodge, id=lodge_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.lodge = lodge
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you! Your review has been posted.')
        else:
            messages.error(request, 'Please fix errors in your review form.')
    return redirect('lodge_detail', lodge_id=lodge.id)

@login_required
def toggle_favorite(request, lodge_id):
    lodge = get_object_or_404(Lodge, id=lodge_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, lodge=lodge)
    
    if not created:
        favorite.delete()
        is_favorited = False
        msg = f'Removed "{lodge.name}" from saved lodges.'
    else:
        is_favorited = True
        msg = f'Saved "{lodge.name}" to your wishlist!'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_favorited': is_favorited, 'message': msg})

    messages.success(request, msg)
    next_url = request.META.get('HTTP_REFERER')
    return redirect(next_url if next_url else 'lodge_detail', lodge_id=lodge.id)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def my_lodges(request):
    if request.user.user_type != 'owner':
        messages.error(request, "Only lodge owners can access this page.")
        return redirect('home')

    lodges = Lodge.objects.filter(owner=request.user)\
                          .prefetch_related('images')\
                          .order_by('-created_at')

    approved_count = lodges.filter(is_approved=True).count()
    pending_count = lodges.filter(is_approved=False).count()

    return render(request, 'lodge/my_lodges.html', {
        'lodges': lodges,
        'approved_count': approved_count,
        'pending_count': pending_count,
    })

@login_required
def owner_profile(request):
    if request.user.user_type != 'owner':
        return redirect('home')

    return render(request, 'lodge/owner_profile.html', {
        'user': request.user,
    })

@login_required
def inquiries(request):
    if request.user.user_type != 'owner':
        return redirect('home')

    return render(request, 'lodge/inquiries.html', {})

@login_required
def add_room(request, lodge_id):
    lodge = get_object_or_404(Lodge, id=lodge_id)

    if request.user != lodge.owner:
        messages.error(request, 'You can only add rooms to your own lodges.')
        return redirect('lodge_detail', lodge_id=lodge.id)

    ImageFormSet = formset_factory(RoomImageForm, extra=4)

    if request.method == 'POST':
        form = RoomForm(request.POST)
        image_formset = ImageFormSet(request.POST, request.FILES)

        if form.is_valid() and image_formset.is_valid():
            uploaded_images = [
                f for f in image_formset if f.cleaned_data.get('image')
            ]

            if len(uploaded_images) < 3:
                messages.error(request, 'Please upload at least 3 photos of the room.')
            else:
                room = form.save(commit=False)
                room.lodge = lodge
                room.save()

                for image_form in uploaded_images:
                    RoomImage.objects.create(
                        room=room,
                        image=image_form.cleaned_data['image']
                    )

                messages.success(request, f'Room "{room.name}" added successfully with {len(uploaded_images)} photos!')
                return redirect('lodge_detail', lodge_id=lodge.id)
    else:
        form = RoomForm()
        image_formset = ImageFormSet()

    return render(request, 'lodge/add_room.html', {
        'lodge': lodge,
        'form': form,
        'image_formset': image_formset,
    })