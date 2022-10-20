from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login_user/', views.login_view, name='login'),
    path('logout_user/', views.logout_view, name='logout'),
    path('contact/', views.contact_view, name='contact'),
]
