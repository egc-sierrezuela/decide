
"""decide URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth import views as auth_views
from base.views import IndexView, VotingInstructionsView, BoothInstrucionsView, VisualizerInstructionsView, StoreInstructionsView
from authentication.views import LoginView, RegisterView
from booth.views import BoothView, get_pagina_inicio

schema_view = get_swagger_view(title='Decide API')

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('votingInstructions', VotingInstructionsView.as_view(), name="votingInstructions"),
    path('boothInstructions', BoothInstrucionsView.as_view(), name="boothInstructions"),
    path('booth/', get_pagina_inicio, name="booth"),
    path('visualizerInstructions', VisualizerInstructionsView.as_view(), name="visualizerInstructions"),
    path('storeInstructions/', StoreInstructionsView.as_view(), name="storeInstructions"),
    path('admin/', admin.site.urls, name="admin"),
    path('doc/', schema_view, name="doc"),
    path('authetication/register-alt', RegisterView, name="register"),
    path('authetication/login-alt', LoginView, name="login"),
    path('authetication/logout-alt',auth_views.LogoutView.as_view(), name="logout"),
    path('gateway/', include('gateway.urls')),
    path('social-auth/', include('social_django.urls', namespace="social")),
]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]
    