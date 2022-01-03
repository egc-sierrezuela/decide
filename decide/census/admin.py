from django.contrib import admin
from django.shortcuts import render,render_to_response
from .models import Census
from django.http import HttpResponse
from . import views
from django.contrib import messages
import csv


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )

    actions = ['import_census','export_census']

    def export_census(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="censo.csv"'
        file = csv.writer(response)
        file.writerow(['Id votante', 'Id votación'])
        ids = []
        for c in queryset:
            #if c.voter_id not in ids:
                file.writerow([c.voter_id, c.voting_id])
                ids.append(c.voter_id)

        self.message_user(request, "Exportación realizada con éxito", level=messages.SUCCESS)

        return response

    def import_census(self,request,queryset):
        return render(request,'censusImport.html')

admin.site.register(Census, CensusAdmin)

