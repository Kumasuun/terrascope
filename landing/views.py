from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.core.mail import send_mail
from .forms import RegisterForm
from .models import CustomUser
import random


# -----------------------
# PUBLIC PAGES
# -----------------------

def index(request):
    return render(request, 'landing/index.html')

def pricing(request):
    return render(request, 'landing/pricing.html')

def about(request):
    return render(request, 'landing/about.html')

def documentation(request):
    return render(request, 'landing/documentation.html')


# -----------------------
# SIGNUP VIEW
# -----------------------

def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'landing/register.html', {'form': form})


# -----------------------
# LOGIN VIEW (Password + OTP)
# -----------------------

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Create 6-digit OTP
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['user_id'] = user.id

            # Send OTP by email
            send_mail(
                'Your TerraScope Login Code',
                f'Your login verification code is: {otp}',
                'no-reply@terrascope.com',
                [user.email],
                fail_silently=False,
            )

            return redirect('verify_otp')

        else:
            return render(request, 'landing/login.html', {'error': 'Invalid credentials'})

    return render(request, 'landing/login.html')


# -----------------------
# OTP VERIFICATION PAGE
# -----------------------

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")
        user_id = request.session.get("user_id")

        if str(stored_otp) == str(entered_otp):
            user = CustomUser.objects.get(id=user_id)
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'landing/verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'landing/verify_otp.html')
