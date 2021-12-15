from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserViewAPI, LogoutViewAPI, RegisterViewAPI, RegisterView


urlpatterns = [
    path('login-api/', obtain_auth_token),
    path('logout-api/', LogoutViewAPI.as_view()),
    path('getuser-api/', GetUserViewAPI.as_view()),
    path('register-api/', RegisterViewAPI.as_view()),
    path('register/', RegisterView.as_view()),
]