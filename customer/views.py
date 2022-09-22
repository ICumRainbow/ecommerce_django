from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            user = form.save()
            login(request, user)
            messages.success(request, 'Success!')
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    context = {'form': form}

    return render(request, 'register.html', context)


def login_user(request):
    context = {

    }

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You've logged in successfully!")
            return redirect('/')
        else:
            messages.success(request, "There was an error logging in, try again!")
            return redirect('login')
    else:
        return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    messages.success(request,'You were logged out!')
    return redirect('/')