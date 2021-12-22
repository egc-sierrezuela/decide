from django.urls import path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_url/', views.VotingUpdate.as_view(), name='voting'),
]
