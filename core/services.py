from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponseRedirect

from customer.forms import ReviewForm
from customer.models import ShippingDetails, Order, OrderItem, ProductReview


def get_query_params(request) -> dict:
    name, category = request.GET.get('name', ''), request.GET.get('category', False)
    query_params = {'name__icontains': name}
    if category:
        query_params['category'] = category
    return query_params


