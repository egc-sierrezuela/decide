from django.contrib import admin
from django.shortcuts import render,render_to_response
from .models import Census
from django.http import HttpResponse
from . import views
from django.contrib import messages
import csv
from django.contrib.auth.models import User


class SexCensusFilter(admin.SimpleListFilter):
    title = "Filtro por género"  # a label for our filter
    parameter_name = 'genero'

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        return [
            ("masculino", "Masculino"),
            ("femenino", "Femenino"),
        ]

    def queryset(self, request, queryset):
        # This is where you process parameters selected by use via filter options:
        if self.value() == "masculino":
            # Para cada censo, busco el user y veo su género. Si el género es masculino
            # entonces añado el c.voting_id en una lista, y después retorno 
            # aquellos objetos mediante el filtro voting_id__in = lista
            lista_censos_masculinos = []
            for c in queryset:
                usuario = User.objects.get(id=c.voter_id)
                persona = usuario.persona
                print(persona.sexo)
                if persona.sexo == "masculino":
                    lista_censos_masculinos.append(c.voter_id)
            print(lista_censos_masculinos)
            return queryset.filter(voter_id__in=lista_censos_masculinos)

        if self.value() == "femenino":
            lista_censos_femeninos = []
            for c in queryset:
                usuario = User.objects.get(id=c.voter_id)
                print(usuario)
                persona = usuario.persona
                if persona.sexo == "femenino":
                    lista_censos_femeninos.append(c.voter_id)
            return queryset.filter(voter_id__in=lista_censos_femeninos)

class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', SexCensusFilter)

    search_fields = ('voter_id',)

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

