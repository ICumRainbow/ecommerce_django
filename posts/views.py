from django.core.paginator import Paginator
from django.shortcuts import render

from posts.filters import PostFilter
from posts.models import Post, PostCategory


def blog(request):
    categories = PostCategory.objects.all()
    posts_by_date = Post.objects.order_by('-created_at')
    post_heading = request.GET.get('heading', '')
    category = request.GET.get('category', False)

    # setting query kwargs depending on the GET request
    query_params = {'heading__icontains': post_heading}
    if category:
        query_params['category_id'] = int(category)
    posts = posts_by_date.filter(**query_params)
    posts = PostFilter(request.GET, queryset=posts)
    paginator = Paginator(posts.qs, 4)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {
        'post_categories': categories,
        'posts_by_date': posts_by_date[:6],
        'page': page,
        'posts': posts,
    }
    return render(request, 'blog.html', context)


def post_details(request, id_):
    categories = PostCategory.objects.all()
    post = Post.objects.get(id=id_)
    posts_by_date = Post.objects.order_by('-created_at')
    related_posts = Post.objects.filter(category=post.category).exclude(id=id_)
    context = {
        'post_categories': categories,
        'posts_by_date': posts_by_date,
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'post.html', context)
