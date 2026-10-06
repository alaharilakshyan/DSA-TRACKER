from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Smart DSA Tracker, {user.username}! Your account has been created.")
            return redirect("dashboard")
        else:
            messages.error(request, "Please fix the errors below to create your account.")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    next_url = request.GET.get("next", "dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect(request.POST.get("next") or "dashboard")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form, "next": next_url})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect("login")
