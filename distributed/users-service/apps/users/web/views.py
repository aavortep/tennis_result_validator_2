from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..internal.user import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role", "SPECTATOR")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return render(request, "register.html", {"form": request.POST})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html", {"form": request.POST})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html", {"form": request.POST})

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role=role,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("home")
        except Exception as e:
            messages.error(request, str(e))

    return render(request, "register.html", {"form": {}})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def profile_view(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.phone = request.POST.get("phone", "")
        user.bio = request.POST.get("bio", "")
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "profile.html", {})


@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home")

    return redirect("profile")
