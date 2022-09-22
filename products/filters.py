import django_filters
from django.db.models import Max, Min
from django import forms
from django.forms import CharField, ModelForm
from django_filters import FilterSet, AllValuesFilter, RangeFilter
from django.forms.widgets import HiddenInput
from django_filters.widgets import RangeWidget

from products.models import Product


class ProductFilter(ModelForm):

    class Meta:
        model = Product
        fields = [
            'category',
            'price',
        ]
        widgets = {
            'price': forms.TextInput(attrs={'type': 'range'})
        }

