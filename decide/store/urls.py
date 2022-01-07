from django.urls import path, include
from .views import PanelView, StoreView
from store import views

urlpatterns = [
    path('', StoreView.as_view(), name='store'),
    path('<int:voting_id>/',PanelView.as_view()),
    # path('superuser/', views.crearSuperUser),
]
