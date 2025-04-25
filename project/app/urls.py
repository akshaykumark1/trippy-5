from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('log-out', views.userlogout, name='userlogout'),
    path('destinations', views.destinations, name='destinations'),
    path('packages', views.packages, name='packages'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('booknow', views.booknow, name='booknow'),
    path('viewdetails/<int:id>/', views.viewdetails, name='viewdetails'),  # Fix for the 'viewdetails' pattern
    path('bookings', views.bookings, name='bookings'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)