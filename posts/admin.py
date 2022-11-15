from collections import defaultdict
from pprint import pprint

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from core.services import get_link_tags, get_category_filter_link_tag
from .models import Post, PostCategory


class PostInlineAdmin(admin.StackedInline):
    model = Post
    classes = ("collapse",)


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    """
    Model to display post categories in admin panel.
    """
    list_display = ("name", "get_posts")
    list_filter = ("name",)
    search_fields = ("name",)
    inlines = (PostInlineAdmin,)

    @admin.display
    def get_posts(self, obj, posts=Post.objects.all()):
        link_tags = get_link_tags(obj=obj, queryset=posts)
        if len(link_tags) < 3:
            return format_html(" ,&nbsp;&nbsp;".join(link_tags))
        else:
            tag = get_category_filter_link_tag(posts.first(), obj.id, len(link_tags))
            sliced_link_tags = " ,&nbsp;&nbsp;".join(link_tags[:3])
            return format_html(sliced_link_tags + f"...({tag})")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Model to display posts in admin panel.
    """
    list_display = ("heading", "get_category")
    list_filter = ("category",)
    search_fields = ("heading", "category__name")
    autocomplete_fields = ("category",)
    fieldsets = (
        ('Author info', {
            'fields': ('author', 'avatar'),
            'classes': ('collapse',)
        }),
        ('Post info', {
            'fields': ('heading', 'category', 'picture', 'content'),
            'classes': ('collapse',)
        })
    )

    @admin.display(description="Category", ordering="category__name")
    def get_category(self, obj):
        url = reverse(f"admin:{obj.category._meta.app_label}_{obj.category._meta.model_name}_change",
                      kwargs={"object_id": obj.category.id})
        category = f'<a href="{url}">{obj.category}</a>'
        return format_html(category)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")
