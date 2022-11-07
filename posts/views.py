from django.core.paginator import Paginator
from django.shortcuts import render

from posts.services import get_blog_page_contents, get_current_post_and_related_posts


def blog_view(request):
    """
    View for blog page.
    """
    post_heading = request.GET.get('heading', '')
    category = request.GET.get('category', False)
    # setting query kwargs depending on the GET request
    query_params = {'heading__icontains': post_heading}
    if category:
        query_params['category_id'] = int(category)
    categories, posts_by_date, posts = get_blog_page_contents(request.GET, query_params)
    paginator = Paginator(posts.qs, 4)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {
        'post_categories': categories,
        'posts_by_date': posts_by_date[:6],
        'page': page,
        'posts': posts,
    }
    return render(request, 'blog/blog.html', context)


def post_details_view(request, id_):
    """
    View for post details page.
    """
    categories, posts_by_date, _ = get_blog_page_contents(request.GET)
    post, related_posts = get_current_post_and_related_posts(id_)
    context = {
        'post_categories': categories,
        'posts_by_date': posts_by_date,
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post.html', context)
