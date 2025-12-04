from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .forms import RegisterForm
from .models import CustomUser

import random
import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO

User = get_user_model()


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
# SIGNUP VIEW + EMAIL OTP
# -----------------------

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # Fix UNIQUE username issue — set username = email
            user.username = user.email
            user.save()

            # Generate signup OTP
            otp = random.randint(100000, 999999)
            request.session['signup_otp'] = otp
            request.session['signup_user_id'] = user.id

            # Email OTP
            send_mail(
                "Your TerraScope Verification Code",
                f"Your verification code is: {otp}",
                "no-reply@terrascope.com",
                [user.email],
                fail_silently=False,
            )

            return redirect("verify_signup_otp")

    else:
        form = RegisterForm()

    return render(request, "landing/register.html", {"form": form})


# -----------------------
# VERIFY SIGNUP OTP
# -----------------------

def verify_signup_otp(request):
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        otp_sent = request.session.get("signup_otp")
        user_id = request.session.get("signup_user_id")

        if str(otp_entered) == str(otp_sent):
            user = User.objects.get(id=user_id)
            auth_login(request, user)

            # Clear session
            del request.session['signup_otp']
            del request.session['signup_user_id']

            return redirect("home")

        return render(request, "landing/verify_signup_otp.html", {"error": "Invalid OTP"})

    return render(request, "landing/verify_signup_otp.html")


# -----------------------
# LOGIN VIEW (Password + 2FA)
# -----------------------

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            auth_login(request, user)

            # If not 2FA verified, redirect to setup
            if not request.session.get('2fa_verified', False):
                return redirect("setup_2fa")

            return redirect("home")

        return render(request, "landing/login.html", {"error": "Invalid credentials"})

    return render(request, "landing/login.html")


# -----------------------
# SETUP 2FA (Google Authenticator)
# -----------------------

@login_required
def setup_2fa(request):
    user = request.user

    totp = pyotp.TOTP(user.otp_secret)

    otp_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="TerraScope Analytics"
    )

    factory = qrcode.image.svg.SvgPathImage
    stream = BytesIO()
    img = qrcode.make(otp_uri, image_factory=factory)
    img.save(stream)

    qr_svg = stream.getvalue().decode('utf-8')

    return render(request, "landing/setup_2fa.html", {"qr_svg": qr_svg})


# -----------------------
# VERIFY GOOGLE AUTHENTICATOR 2FA
# -----------------------

@login_required
def verify_2fa(request):
    user = request.user

    if request.method == "POST":
        code = request.POST.get("code")

        if user.get_totp().verify(code):
            request.session['2fa_verified'] = True
            return redirect("home")

        return render(request, "landing/verify_2fa.html", {"error": "Invalid verification code"})

    return render(request, "landing/verify_2fa.html")
