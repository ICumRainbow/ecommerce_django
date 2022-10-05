from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blog, name='blog'),
    path('post/<int:id>', views.post_details, name='post'),
]

