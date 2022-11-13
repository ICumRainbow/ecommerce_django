from django.db import models
from django.db.models import F, ExpressionWrapper


def get_query_params(request) -> dict:
    """
    Gets query kwargs from request and returns them as dict.
    """
    name, category = request.GET.get('name', ''), request.GET.get('category', False)
    query_params = {'name__icontains': name}
    if category:
        query_params['category'] = category
    return query_params


def annotate_with_discount_prices(queryset: models.QuerySet):
    return queryset.annotate(
        discount_percent=ExpressionWrapper(
            (100 - F('product__discount_rate')) / 100.0,
            output_field=models.FloatField()
        ),
        discount_price=ExpressionWrapper(
            F('product__price') * F('discount_percent'),
            output_field=models.FloatField()
        )
    )
