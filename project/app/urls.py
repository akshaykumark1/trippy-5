from django.urls import path
from .import views

urlpatterns = [
    path('home',views.home,name='admin'),
    path('',views.signin,name='signin'),
    path('signup',views.signup,name='signup'),

]
