from django.urls import path
from knox import views as knox_views

from accounts.api import RegisterAPI, LoginAPI


urlpatterns = [
    path('api/accounts/register', RegisterAPI.as_view(), name='register'),
    path('api/accounts/login', LoginAPI.as_view(), name='login'),
    path('api/accounts/logout', knox_views.LogoutView.as_view(), name='logout')
]
