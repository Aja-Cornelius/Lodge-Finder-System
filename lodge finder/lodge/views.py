# lodge/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import StudentSignUpForm, OwnerSignUpForm
from .forms import LodgeForm, LodgeImageForm
from django.forms import formset_factory
from .models import Lodge, Amenity, LodgeImage 
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.shortcuts import redirect


def home(request):
    return render(request, 'lodge/landing.html')

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
    return render(request, 'lodge/student_dashboard.html')

@login_required
def owner_dashboard(request):
    if request.user.user_type != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')

    # Get only this owner's lodges
    my_lodges = Lodge.objects.filter(owner=request.user)

    # Calculate real stats
    total_lodges = my_lodges.count()
    approved = my_lodges.filter(is_approved=True).count()
    pending = my_lodges.filter(is_approved=False).count()

    context = {
        'my_lodges': my_lodges,
        'total_lodges': total_lodges,
        'approved': approved,
        'pending': pending,
    }

    return render(request, 'lodge/owner_dashboard.html', context)

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
    lodges = Lodge.objects.filter(is_approved=True)

    # Apply filters
    location = request.GET.get('location')
    room_type = request.GET.get('room_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if location:
        lodges = lodges.filter(location__icontains=location)
    if room_type:
        lodges = lodges.filter(room_type=room_type)
    if min_price:
        try:
            lodges = lodges.filter(price_per_year__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            lodges = lodges.filter(price_per_year__lte=float(max_price))
        except ValueError:
            pass

    return render(request, 'lodge/search_results.html', {
        'lodges': lodges,
        'filters': request.GET,  # ← This line is very important!
    })

def lodge_detail(request, lodge_id):
    lodge = get_object_or_404(Lodge, id=lodge_id, is_approved=True)
    images = lodge.images.all()
    return render(request, 'lodge/lodge_detail.html', {
        'lodge': lodge,
        'images': images,
    })


def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
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