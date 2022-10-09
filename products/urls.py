from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product_details/<int:id>', views.product_details, name='product_details'),
    path('shop-grid/', views.shop_grid, name='shop_grid'),
    path('cart/', views.cart, name='cart'),
    path('update_item/', views.update_item_view, name='update_item'),
    path('like_item/', views.like_item_view, name='like_item'),
    path('checkout/', views.checkout_view, name='checkout'),
]
