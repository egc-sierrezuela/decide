from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views

from .views import GetUserViewAPI, LogoutViewAPI, RegisterViewAPI, RegisterView, LoginView, SuccessView


urlpatterns = [
    path('login-api/', obtain_auth_token),
    path('logout-api/', LogoutViewAPI.as_view()),
    path('getuser-api/', GetUserViewAPI.as_view()),
    path('register-api/', RegisterViewAPI.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view(),name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('login-success', SuccessView.as_view(),name="login-success")
]