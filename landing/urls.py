


from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('documentation/', views.documentation, name='documentation'),
    
    # Correct signup route
    path('signup/', views.signup, name='signup'),

    # Correct login route
    path('login/', views.login_view, name='login'),
    
    # OTP
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]
