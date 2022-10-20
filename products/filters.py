from django_filters import NumberFilter, FilterSet, CharFilter
from django.db.models import Max, Min
from django.forms import CharField

from products.models import Product


class ProductFilter(FilterSet):
    price = Product.objects.all().select_related().aggregate(Min('price'), Max('price'))
    name = CharFilter(lookup_expr='icontains')
    price_min = price['price__min']
    price_max = price['price__max']
    price__gt = NumberFilter(field_name='price', lookup_expr='gte')
    price__lt = NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'price__gt',
            'price__lt',
        ]
