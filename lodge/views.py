# lodge/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from .forms import StudentSignUpForm, OwnerSignUpForm
from .forms import LodgeForm, LodgeImageForm
from django.forms import formset_factory
from .models import Lodge, Amenity, LodgeImage 
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import Http404   # ← ADD THIS LINE
from django.db.models import Q


def home(request):
    # Fetch the 3 most recent approved lodges for the landing page
    recent_lodges = Lodge.objects.filter(is_approved=True)\
                         .prefetch_related('images', 'amenities')\
                         .select_related('owner')\
                         .order_by('-created_at')[:3]

    return render(request, 'lodge/landing.html', {
        'recent_lodges': recent_lodges,
    })

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Saves the user to the database
            login(request, user)  # Automatically logs them in
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('student_dashboard')
        # else:
        #     messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentSignUpForm()
    return render(request, 'lodge/student_signup.html', {'form': form})

def owner_signup(request):
    if request.method == 'POST':
        form = OwnerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Saves the user to the database
            login(request, user)  # Automatically logs them in
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
        
        # Try to authenticate (works with username or email)
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

    # Real stats from the database
    total_lodges = approved_lodges.count()
    total_locations = approved_lodges.values('location').distinct().count()
    total_room_types = approved_lodges.values('room_type').distinct().count()

    # Fetch the 6 most recent approved lodges for the student dashboard
    recommended_lodges = approved_lodges\
                              .prefetch_related('images', 'amenities')\
                              .select_related('owner')\
                              .order_by('-created_at')[:6]

    return render(request, 'lodge/student_dashboard.html', {
        'recommended_lodges': recommended_lodges,
        'total_lodges': total_lodges,
        'total_locations': total_locations,
        'total_room_types': total_room_types,
    })

@login_required
def owner_dashboard(request):
    if request.user.user_type != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')

    # Optimized query for owner dashboard
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

    ImageFormSet = formset_factory(LodgeImageForm, extra=3)  # Allow 3 photos

    if request.method == 'POST':
        form = LodgeForm(request.POST)
        image_formset = ImageFormSet(request.POST, request.FILES)

        if form.is_valid() and image_formset.is_valid():
            lodge = form.save(commit=False)
            lodge.owner = request.user
            lodge.save()
            form.save_m2m()  # Save amenities

            # Save images
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
    # Optimized query - prefetch related data to avoid N+1 queries
    lodges = Lodge.objects.filter(is_approved=True)\
                          .select_related('owner')\
                          .prefetch_related('images', 'amenities')\
                          .order_by('-created_at')

    location = request.GET.get('location')
    room_type = request.GET.get('room_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if location:
        lodges = lodges.filter(Q(location__icontains=location) | Q(name__icontains=location))
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
    
    # Pagination
    paginator = Paginator(lodges, 6) # 6 lodges per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lodge/search_results.html', {
        'page_obj': page_obj,
        'total_results': total_results,
        'filters': request.GET,
    })
def lodge_detail(request, lodge_id):
    # This will show a nice 404 if the lodge doesn't exist or is not approved
    lodge = get_object_or_404(Lodge, id=lodge_id)

    # Optional: Only show approved lodges to students (but allow owners to see their own)
    if not lodge.is_approved and lodge.owner != request.user:
        raise Http404("This lodge is not yet approved.")

    images = lodge.images.all()

    return render(request, 'lodge/lodge_detail.html', {
        'lodge': lodge,
        'images': images,
    })


def logout_view(request):
    logout(request)
    return redirect('home')  # or 'login' or wherever you want to send users

@login_required
def my_lodges(request):
    if request.user.user_type != 'owner':
        messages.error(request, "Only lodge owners can access this page.")
        return redirect('home')

    # Get only lodges belonging to this owner
    lodges = Lodge.objects.filter(owner=request.user).order_by('-created_at')

    return render(request, 'lodge/my_lodges.html', {
        'lodges': lodges,
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

    # Later: fetch real inquiries
    return render(request, 'lodge/inquiries.html', {})