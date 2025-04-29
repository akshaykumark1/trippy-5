from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


      
def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            if  user.is_superuser:
                return redirect('admin')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'signin.html')
def signup(request):
    if request.method == 'POST':  
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        if not username or not email or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            # Corrected line to use create_user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('signin')  

    return render(request, "signup.html")


def userlogout(request):
    request.session.flush()
    return render(request, 'home.html')

# ---------------------------------------------------------------------

def home(request):
    packages = Package.objects.all()[:6]  # Show latest 6 packages on homepage
    reviews = Review.objects.all()  # All reviews for testimonials
    context = {
    'Packages': packages,
    'Reviews': reviews,
    }
    return render(request,'home.html',context)

def viewpackagedetails(request, id):
    package = get_object_or_404(Package, id=id)
    # Get related packages (you can customize this query as needed)
    related_packages = Package.objects.exclude(id=id).order_by('-start_date')[:3]
    context = {
        'package': package,
        'related_packages': related_packages
    }
    return render(request, 'viewpackagedetails.html', context)
def bookings(request, id):  # id = Package id
    package = get_object_or_404(Package, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        guests = request.POST.get('guests')
        message = request.POST.get('message')

        # For demo, assume number_of_people is parsed from `guests`
        number_of_people = 1 if guests == "1" else 2 if guests == "2" else 4 if guests == "3-4" else 5

        customer = Customer.objects.get(user=request.user)

        booking = Booking.objects.create(
            customer=customer,
            travel_package=package,
            number_of_people=number_of_people,
            total_price=number_of_people * package.price,
            status='Pending'
        )

        return redirect('booking_revi', id=package.id)  # or wherever you want to go after

    return render(request, 'bookings.html', {'package': package})


def booking_review(request, id):  # id = Package id
    package = get_object_or_404(Package, id=id)

    if request.method == 'POST':
        # Check if the customer exists
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            # If no customer profile exists, show an error message
            messages.error(request, 'You need to create a customer profile before making a booking.')
            return redirect('profile_create')  # Redirect to the profile creation page (you need to create this view)

        # Extract form data
        number_of_people = request.POST.get('guests')

        if not number_of_people or not number_of_people.isdigit() or int(number_of_people) <= 0:
            messages.error(request, 'Please enter a valid number of guests.')
            return redirect('booking_review', id=id)

        # Calculate total price based on number of people
        total_price = int(number_of_people) * package.price

        # Create a temporary booking object or simply pass this data to the confirmation page
        context = {
            'package': package,
            'number_of_people': number_of_people,
            'total_price': total_price,
        }
        return render(request, 'booking_confirm.html', context)

    return render(request, 'booking_review.html', {'package': package})

def profile_create(request):
    if request.method == 'POST':
        # Get the form data manually from the request
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Check if data is provided
        if not phone or not address:
            messages.error(request, "Both phone and address are required.")
            return redirect('profile_create')

        # Create and save the customer profile
        try:
            customer = Customer.objects.create(user=request.user, phone=phone, address=address)
            customer.save()
            messages.success(request, "Profile created successfully.")
            return redirect('home')  # Redirect after successful profile creation
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('profile_create')
    
    return render(request, 'profile.html')

def confirm_booking(request, id):  # id = Package id
    package = get_object_or_404(Package,id=id)

    if request.method == 'POST':
        # Check if the customer exists
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, 'You need to create a customer profile before confirming the booking.')
            return redirect('profile_create')  # Redirect to the profile creation page

        # Extract form data from the session or POST
        number_of_people = request.POST.get('guests')
        total_price = int(number_of_people) * package.price

        # Create a new booking object
        booking = Booking.objects.create(
            customer=customer,
            package=package,
            number_of_people=number_of_people,
            total_price=total_price,
            status='Confirmed',  # Mark as confirmed
        )

        messages.success(request, 'Your booking has been confirmed successfully!')
        return redirect('my_bookings')  # Redirect to a success page

    return render(request, 'booking_confirm.html', {'package': package})

def my_bookings(request):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if the user is not authenticated
    try:
        # Get the customer's profile
        customer = request.user.customer  # Assuming each user has a corresponding Customer profile
    except Customer.DoesNotExist:
        # If no customer profile exists, show an error message
        messages.error(request, 'You need to create a customer profile to view your bookings.')
        return redirect('profile_create')  # Redirect to profile creation page

    # Retrieve all bookings for the logged-in customer
    bookings = Booking.objects.filter(customer=customer)

    return render(request, 'my_bookings.html', {'bookings': bookings})


def add_vehicle_admin(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        package_id = request.POST.get('package')
        price = request.POST.get('price')
        
        try:
            package = Package.objects.get(id=package_id)
            vehicle = Vehicle(name=name, package=package, price=price)
            vehicle.save()
            messages.success(request, 'Vehicle added successfully!')
            return redirect('/admin/vehicles/')  # Redirect to vehicles list
        except Exception as e:
            messages.error(request, f'Error adding vehicle: {str(e)}')
            
    packages = Package.objects.all()
    context = {
        'packages': packages,
    }
    return render(request, 'add_vehicle_admin.html', context)



def addpackages(request):
    if request.method == 'POST':
        try:
            # Extract form data
            title = request.POST.get('title')
            duration_days = request.POST.get('duration_days')
            description = request.POST.get('description')
            included = request.POST.get('included')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            # Create new package object
            package = Package(
                title=title,
                duration_days=duration_days,
                description=description,
                included=included,
                start_date=start_date,
                end_date=end_date
            )
            
            # Handle image uploads
            if 'image' in request.FILES:
                package.image = request.FILES['image']
            
            if 'image2' in request.FILES:
                package.image2 = request.FILES['image2']
            
            if 'image3' in request.FILES:
                package.image3 = request.FILES['image3']
            
            # Save package to database
            package.save()
            
            messages.success(request, f'Package "{title}" added successfully!')
            return redirect('/admin/packages/')  # Redirect to packages list
        except Exception as e:
            messages.error(request, f'Error adding package: {str(e)}')
    
    return render(request, 'admin/addpackages.html')



def vehicles(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles.html', {'vehicles': vehicles})

def packages(request):
    return render(request,'packages.html')
def aboutus(request):
    return render(request,'aboutus.html')

def booknow(request):
    return render(request,'booknow.html')    


def admin(request):
    return render(request,'admin/admin.html')




def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'Cancelled'
    booking.save()
    return redirect('my_bookings')


    ######################################admin##########################################

def booking_list(request):
    bookings = Booking.objects.select_related('customer', 'travel_package')
    return render(request, 'adminpages/booking_list.html', {'bookings': bookings})

def customer_list(request):
    customers = Customer.objects.select_related('user')
    return render(request, 'adminpages/customer_list.html', {'customers': customers})

def package_list(request):
    packages = Package.objects.all()
    return render(request, 'adminpages/package_list.html', {'packages': packages})

def review_list(request):
    reviews = Review.objects.select_related('customer')
    return render(request, 'adminpages/review_list.html', {'reviews': reviews})

def vehicle_list(request):
    vehicles = Vehicle.objects.select_related('package')
    return render(request, 'adminpages/vehicle_list.html', {'vehicles': vehicles})
