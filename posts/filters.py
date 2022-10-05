from django.forms import CharField, IntegerField
from django_filters import FilterSet

from posts.models import Post


class PostFilter(FilterSet):

    class Meta:
        model = Post
        fields = {
            'heading',
            'category',
        }
