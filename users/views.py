from django.shortcuts import render, redirect
from users.forms import CustomRegistrationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages


def sign_up(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 🔑 auto login
            messages.success(request, "Registration successful")
            return redirect('home')
    else:
        form = CustomRegistrationForm()

    return render(request, 'registration/register.html', {"form": form})


def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


def sign_out(request):
    logout(request)
    return redirect('sign-in')
