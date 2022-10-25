from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blog, name='blog'),
    path('post/<int:id_>', views.post_details, name='post'),
]

