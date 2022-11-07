from customer.models import Order, OrderItem


# getting items from the order when user is not registered
def get_current_order_items(request):
    """
    Getting order items for a newly registered user, if he added any before registration.
    """
    order = Order.objects.get(session_id=request.session.session_key)
    order_items = OrderItem.objects.filter(order=order)
    return order, order_items


def transfer_order_items(request, user, order_items):
    """
    Transferring the items to order of a newly registered user.
    """
    session_id = request.session.session_key

    order_kwargs = {'customer': user, 'completed': False} if request.user.id else {'session_id': session_id,
                                                                                   'completed': False}
    order, created = Order.objects.get_or_create(**order_kwargs)
    order.session_id = session_id

    for item in order_items:
        OrderItem.objects.get_or_create(order=order, product=item.product, quantity=item.quantity)

    order.customer = user


def get_or_create_order_for_login(user):
    """
    Getting or creating order for a user after login.
    """
    Order.objects.get_or_create(customer_id=user.id, completed=False, session_id=None)
