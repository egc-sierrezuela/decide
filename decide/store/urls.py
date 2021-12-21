from django.urls import path, include
from .views import PanelView, StoreView


urlpatterns = [
    path('', StoreView.as_view(), name='store'),
    path('<int:voting_id>/',PanelView.as_view()),
]
