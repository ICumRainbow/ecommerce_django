from math import ceil

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from posts.models import Post, PostCategory


def blog(request):
    categories = PostCategory.objects.all().select_related()
    posts_sorted_by_date = Post.objects.all().order_by('-created_at')[:6]
    posts = Post.objects.all()

    try:
        post_name = request.GET['heading']
        category = request.GET['category']
        posts_object = Post.objects.filter(Q(heading__icontains=post_name, category__id=category))
    except (MultiValueDictKeyError, ValueError):
        posts_object = posts_sorted_by_date

    # filtered_posts = PostFilter(
    #     request.GET,
    #     queryset=posts
    # )
    paginator = Paginator(posts_object, 4)

    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'categories': categories,
        'posts_by_date': posts_sorted_by_date,
        'page_obj': page_obj,
    }

    return render(request, 'blog.html', context)




# def blog_search(request):
#     post_categories = PostCategory.objects.all()
#     posts_sorted_by_date = Post.objects.all().order_by('-created_at')[:6]
#
#
#
#     search_query = request.GET['post_name']
#
#     page_number = request.GET.get('page', 1)
#     products_paginated = Paginator(post_object, 4)
#     page_obj = products_paginated.get_page(page_number)
#     page_count = ceil(len(post_object) / 9)
#     page_count_range = range(1, page_count + 1)
#
#     context = {
#         'page_obj': page_obj,
#         'page_count_range': page_count_range,
#         'search_query': search_query,
#         'posts_by_date': posts_sorted_by_date,
#         'post_categories': post_categories,
#     }
#
#     return render(request, 'blog-search.html', context)


def post_details(request, id):
    post = Post.objects.get(id=id)
    related_posts = Post.objects.filter(category=post.category).exclude(id=id)
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'post.html', context)
