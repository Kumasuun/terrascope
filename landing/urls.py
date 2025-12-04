from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    # Static pages
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('documentation/', views.documentation, name='documentation'),

    # Auth
    path('signup/', views.register, name='signup'),
    path('login/', views.login_view, name='login'),

    # Email OTP (first factor)
    path("verify-otp/", views.verify_signup_otp, name="verify_signup_otp"),


    # Google Authenticator (Second factor)
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
]
