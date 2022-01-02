from django.contrib import admin
from .models import Census
from django.http import HttpResponse
import csv



def export_census(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="censo.csv"'
    file = csv.writer(response)
    file.writerow(['Id votante'])
    ids = []
    for c in queryset:
        if c.voter_id not in ids:
            file.writerow([c.voter_id])
            ids.append(c.voter_id)

    return response

class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )
    actions = [export_census]


admin.site.register(Census, CensusAdmin)
