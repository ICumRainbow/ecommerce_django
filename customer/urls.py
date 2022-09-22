from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login_user/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout'),

]
