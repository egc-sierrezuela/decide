from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class IndexView(TemplateView):
    template_name = 'inicio.html'

class VotingInstructionsView(TemplateView):
    template_name = 'voting.html'

class BoothInstrucionsView(TemplateView):
    template_name = 'booth.html'

class VisualizerInstructionsView(TemplateView):
    template_name = 'visualizer.html'