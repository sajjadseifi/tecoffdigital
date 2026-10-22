from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.auth_page, name="auth_login"),
    path("logout/", views.auth_logout, name="auth_logout"),
]