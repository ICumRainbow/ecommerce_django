from collections import defaultdict
from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.db.models import F, ExpressionWrapper
from django.urls import reverse

import posts.models
import products.models


def get_query_params(request: WSGIRequest) -> dict:
    """
    Returns query kwargs received from request as dict.
    """
    name, category = request.GET.get('name', ''), request.GET.get('category', False)
    query_params = {'name__icontains': name}
    if category:
        query_params['category'] = category
    return query_params


def annotate_with_discount_prices(queryset: models.QuerySet) -> models.QuerySet:
    """
    Returns Product queryset annotated with discount percentage and prices according to their discount percentage.
    """
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


def get_link_tags(obj: Union[posts.models.PostCategory, products.models.Category] = None,
                  queryset=None) -> list:
    """
    Returns HTML <a> tags referring to obj's (category's) child objects.
    """
    # не могу придумать как минимизировать запросы: сейчас по запросу на категорию
    tags = [
        f'<a href="{reverse(f"admin:{object_._meta.app_label}_{object_._meta.model_name}_change", kwargs={"object_id": object_.id})}">{str(object_)}</a>'
        for object_ in queryset.filter(category=obj.id)
    ]
    return tags


def get_category_filter_link_tag(instance, id_, content):
    return f'<a href="{reverse(f"admin:{instance._meta.app_label}_{instance._meta.model_name}_changelist")}' \
           f'?category__id__exact={id_}">{content}</a> '
