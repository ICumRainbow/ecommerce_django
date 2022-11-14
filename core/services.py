from collections import defaultdict
from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.db.models import F, ExpressionWrapper

import posts.models
import products.models


def get_query_params(request: WSGIRequest) -> dict:
    """
    Gets query kwargs from request and returns them as dict.
    """
    name, category = request.GET.get('name', ''), request.GET.get('category', False)
    query_params = {'name__icontains': name}
    if category:
        query_params['category'] = category
    return query_params


def annotate_with_discount_prices(queryset: models.QuerySet) -> models.QuerySet:
    """
    Gets products' prices according to their discount percentage.
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


def get_child_objects_with_links(queryset: models.QuerySet = None,
                                 obj: Union[posts.models.PostCategory, products.models.Category] = None,
                                 posts_: bool = False,
                                 products_: bool = False) -> list:
    """
    Gets child objects of a given queryset.
    """
    if products_:
        app = 'products'
        table = 'product'
    else:
        app = 'posts'
        table = 'post'

    child_objects = defaultdict(list)
    child_objects_ids = defaultdict(list)
    for object_ in queryset:
        id_ = str(object_.id)
        child_objects[object_.category_id].append(object_.heading) if posts_ else \
            child_objects[object_.category_id].append(object_.name)

        child_objects_ids[object_.category_id].append(id_)

    child_objects = child_objects[obj.id]
    child_objects_ids = child_objects_ids[obj.id]
    child_objects_with_links = []

    for object_, _id in zip(child_objects, child_objects_ids):
        # queryset.model._meta.app_label
        url = f'http://127.0.0.1:8000/admin/{app}/{table}/{_id}/change'
        object_ = f'<a href="{url}">{object_}</a>'
        child_objects_with_links.append(object_)
    return child_objects_with_links
