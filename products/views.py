from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.shortcuts import render
from django.db.models import Min, Max

from math import ceil

from django_filters import RangeFilter

from posts.models import Post
from products.models import Category, Product
from .filters import ProductFilter


def index(request):
    categories = Category.objects.all()
    for ctg in categories:
        ctg.slugified_name = ''.join(filter(str.isalnum, ctg.name))

    products = Product.objects.all().order_by('created_at')
    query_for_posts_sorted_by_date = Post.objects.all().query
    query_for_posts_sorted_by_date.order_by = ['-created_at']
    posts_sorted_by_date = QuerySet(query=query_for_posts_sorted_by_date, model=Post)

    context = {
        'categories': categories,
        'products': products,
        'posts_by_date': posts_sorted_by_date,
    }

    return render(request, 'index.html', context)


def shop_details(request):
    return render(request, 'shop-details.html')


def shop_grid(request):
    print(request.GET)
    categories = Category.objects.all()

    products_sorted_by_date = Product.objects.all().order_by('-created_at')[:6]
    products_with_discount = Product.objects.all().filter(discount=True)
    products = Product.objects.all()

    filtered_products = ProductFilter()
    print('HERE')
    print(filtered_products)
    print('HERE')
    page_number = request.GET.get('page', 1)
    products_paginated = Paginator(filtered_products, 9)
    page_obj = products_paginated.get_page(page_number)
    page_count = ceil(len(filtered_products.qs) / 9)
    page_count_range = range(1, page_count + 1)

    context = {
        'categories': categories,
        'products': products,
        'products_with_discount': products_with_discount,
        'products_sorted_by_date': products_sorted_by_date,
        'page_obj': page_obj,
        'page_count_range': page_count_range,
        'filtered_products': filtered_products,
    }
    return render(request, 'shop-grid.html', context)

