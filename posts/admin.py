from collections import defaultdict
from pprint import pprint

from django.contrib import admin
from django.utils.html import format_html

from core.services import get_child_objects_with_links
from .models import Post, PostCategory


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    """
    Model to display post categories in admin panel.
    """
    list_display = ("name", "get_posts")
    list_filter = ("name",)
    search_fields = ("name",)

    @admin.display
    def get_posts(self, obj, posts=Post.objects.all()):
        child_posts_with_links = get_child_objects_with_links(queryset=posts, obj=obj)
        if len(child_posts_with_links) < 3:
            return format_html(" ,&nbsp;&nbsp;".join(child_posts_with_links))
        else:
            category_url = (
                    "http://127.0.0.1:8000/admin/posts/post/?category__id__exact=" + str(obj.id)
            )
            category_link = f'<a href="{category_url}">{len(child_posts_with_links)}</a>'
            first_three_child_posts = " ,&nbsp;&nbsp;".join(child_posts_with_links[:3])
            return format_html(first_three_child_posts + f"...({category_link})")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Model to display posts in admin panel.
    """
    list_display = ("heading", "get_category")
    list_filter = ("category",)
    search_fields = ("heading", "category__name")
    autocomplete_fields = ("category",)

    def get_urls(self):
        result = super().get_urls()
        pprint(result)
        return result

    @admin.display(description="Category", ordering="category__name")
    def get_category(self, obj):
        url = (
                "http://127.0.0.1:8000/admin/posts/postcategory/"
                + str(obj.category.id)
                + "/change/"
        )
        category = f'<a href="{url}">{obj.category}</a>'
        return format_html(category)
