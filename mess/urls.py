from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('loginqr/', views.QRlogin_view, name='loginqr'),
    path('vendorscan/', views.vendorscan, name='vendorscan'),
]