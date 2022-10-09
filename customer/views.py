from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm
from .models import Order, OrderItems


def get_current_order_items(request):
    order = Order.objects.get(session_id=request.session.session_key)
    order_items = OrderItems.objects.filter(order=order)
    return order_items


def transfer_order_items(request, user, order_items):
    session_id = request.session.session_key
    if request.user.is_authenticated:
        new_order, created = Order.objects.get_or_create(customer=user)
    else:
        new_order, created = Order.objects.get_or_create(session_id=session_id)
    for item in order_items:
        OrderItems.objects.get_or_create(order=new_order, product=item.product, quantity=item.quantity)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        order = Order.objects.get(session_id=request.session.session_key)
        order_items = get_current_order_items(request)
        if form.is_valid():
            user = form.save()
            login(request, user)
            transfer_order_items(request, user, order_items)
            order.customer = user
            messages.success(request, 'Success!')
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    context = {'form': form}

    return render(request, 'register.html', context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        order_items = get_current_order_items(request)
        if user is not None:
            login(request, user)
            transfer_order_items(request, user, order_items)
            messages.success(request, "You've logged in successfully!")
            return redirect('/')
        else:
            messages.success(request, "There was an error logging in, try again!")
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You were logged out!')
    return redirect(request.META.get('HTTP_REFERER'))


def contact(request):
    return render(request, 'contact.html')
