from django_filters import NumberFilter, FilterSet, CharFilter
from django.db.models import Max, Min, F
from django.forms import CharField

from products.models import Product


class ProductFilter(FilterSet):
    price = Product.objects.all().select_related('category').aggregate(price__min=Min((F('price')*(100 - F('discount_rate')))/100), price__max=Max((F('price')*(100 - F('discount_rate')))/100))
    name = CharFilter(lookup_expr='icontains')
    price_min = price['price__min']
    price_max = price['price__max']
    price__gt = NumberFilter(field_name=Min((F('price')*(100 - F('discount_rate')))/100), lookup_expr='gte')
    price__lt = NumberFilter(field_name='price_max', lookup_expr='lte')

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'price__gt',
            'price__lt',
        ]
