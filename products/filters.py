from django.db import models
from django_filters import NumberFilter, FilterSet, CharFilter
from django.db.models import Max, Min, F, ExpressionWrapper

from products.models import Product, Category


class ProductFilter(FilterSet):
    price = Product.objects.aggregate(
        price__min=Min((F('price') * (100 - F('discount_rate'))) / 100),
        price__max=Max((F('price') * (100 - F('discount_rate'))) / 100)
    )
    # price = Product.objects.all().aggregate(price__min=Min('price'), price__max=Max('price'))
    name = CharFilter(lookup_expr='icontains')
    category = Category.objects.select_related()
    price_min = price['price__min']
    price_max = price['price__max']
    price__gt = NumberFilter(field_name='discount_price', lookup_expr='gte')
    price__lt = NumberFilter(field_name='discount_price', lookup_expr='lte')

    def filter_queryset(self, queryset):
        queryset = queryset.annotate(
            discount_percent=ExpressionWrapper(
                (100 - F('discount_rate')) / 100.0,
                output_field=models.FloatField()
            ),
            discount_price=ExpressionWrapper(
                F('price') * F('discount_percent'),
                output_field=models.FloatField()
            )
        )
        return super().filter_queryset(queryset)

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'price__gt',
            'price__lt',
        ]
