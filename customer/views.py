from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm, ContactForm
from .services import get_current_order_items, transfer_order_items, get_or_create_order_for_login


def register_view(request):
    """
    View for registration.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        # we get the items user could've added to the cart before registering
        _, order_items = get_current_order_items(request)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # transferring the items got from the get_current_order_items function to the newly registered user's order
            transfer_order_items(request, user, order_items)
            messages.success(request, 'Success!')
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    context = {'form': form}

    return render(request, 'customer/register.html', context)


def login_view(request):
    """
    View for logging in.
    """
    print(request.GET)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            previous_page = request.GET['next']
            print(previous_page)
            get_or_create_order_for_login(user)
            login(request, user)
            messages.success(request, "You've logged in successfully!")
            return redirect(previous_page)
        else:
            messages.success(request, "There was an error logging in, try again!")
            return render(request, 'customer/login.html')
    else:
        return render(request, 'customer/login.html')


def logout_view(request):
    """
    View for logging out.
    """
    logout(request)
    messages.success(request, 'You were logged out!')
    # redirecting to the current page
    return redirect(request.META.get('HTTP_REFERER'))


def contact_view(request):
    """
    View for contact page.
    """
    form = ContactForm(request.POST)
    # because there can be two POST forms on one page (EmailSub form), we specify the IF condition
    if request.method == 'POST' and 'name' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your message! We will answer in 24 hours!")
        else:
            messages.success(request, "Something went wrong, please try again!")
            print(form.errors.as_data)

    context = {
        "form": form,
    }

    return render(request, 'customer/contact.html', context)
