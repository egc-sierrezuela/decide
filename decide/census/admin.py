from django.contrib import admin
from django.shortcuts import render,render_to_response

from .models import Census
from django.http import HttpResponse
from . import views

def import_census(modeladmin,request,queryset):
    return render(request,'censusImport.html')

class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )
    actions = [import_census]

admin.site.register(Census, CensusAdmin)

