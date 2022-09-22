from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop-details/', views.shop_details, name='shop_details'),
    path('shop-grid/', views.shop_grid, name='shop_grid'),
]
