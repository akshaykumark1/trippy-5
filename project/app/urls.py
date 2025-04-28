from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('log-out', views.userlogout, name='userlogout'),
    path('packages', views.packages, name='packages'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('booknow', views.booknow, name='booknow'),
    path('viewpackagedetails/<int:id>', views.viewpackagedetails, name='viewpackagedetails'),
    path('bookings/<id>', views.bookings, name='bookings'),
    path(' /<id>', views.booking_review, name='booking_revi'),
    path('profile/create/', views.profile_create, name='profile_create'),  # Add this line
    path('confirm/<id>', views.confirm_booking, name='confirm_booking'),
    path('my_bookings', views.my_bookings, name='my_bookings'),

    ####################################################################################################3
    path('admi',views.admin, name='admin'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('addpackages/',views.addpackages,name='addpackages'),
    path('vehicles/',views.vehicles,name='vehicles'),
]

    




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)