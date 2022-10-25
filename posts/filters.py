from django.forms import CharField, IntegerField
from django_filters import FilterSet, CharFilter

from posts.models import Post


class PostFilter(FilterSet):
    heading = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Post
        fields = {
            'heading',
            'category',
        }
