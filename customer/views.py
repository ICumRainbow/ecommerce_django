from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm, ContactForm
from .models import Order, OrderItem


# getting items from the order when user is not registered
def get_current_order_items(request):
    order = Order.objects.get(session_id=request.session.session_key)
    order_items = OrderItem.objects.filter(order=order)
    return order, order_items


# transferring the items to order of a newly registered user
def transfer_order_items(request, user, order_items):
    session_id = request.session.session_key

    order_kwargs = {'customer': user, 'completed': False} if request.user.id else {'session_id': session_id, 'completed': False}
    order, created = Order.objects.get_or_create(**order_kwargs)
    order.session_id = session_id

    for item in order_items:
        OrderItem.objects.get_or_create(order=order, product=item.product, quantity=item.quantity)


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        # we get the items user could've added to the cart before registering
        order, order_items = get_current_order_items(request)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # transferring the items got from the get_current_order_items function to the newly registered user's order
            transfer_order_items(request, user, order_items)
            order.customer = user
            messages.success(request, 'Success!')
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    context = {'form': form}

    return render(request, 'register.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            Order.objects.get_or_create(customer_id=user.id, completed=False, session_id=None)
            login(request, user)
            messages.success(request, "You've logged in successfully!")
            return redirect('index')
        else:
            messages.success(request, "There was an error logging in, try again!")
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You were logged out!')
    # redirecting to the current page
    return redirect(request.META.get('HTTP_REFERER'))


def contact_view(request):
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

    return render(request, 'contact.html', context)
