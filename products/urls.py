from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('product_details/<int:id_>', views.product_details_view, name='product_details'),
    path('shop-grid/', views.shop_grid_view, name='shop_grid'),
    path('cart/', views.cart_view, name='cart'),
    path('update_item/', views.update_item_view, name='update_item'),
    path('like_item/', views.like_item_view, name='like_item'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('liked_products/', views.liked_products_view, name='liked_products'),
]
