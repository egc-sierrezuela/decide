from django.core.exceptions import ValidationError
from voting.models import Voting


def validation_census_voting_id(value):
    votings_exitentes=Voting.objects.all()
    ids=[]
    for i in range(0,len(votings_exitentes)):
        ids.append(int(votings_exitentes[i].id))
    if value not in ids:
        raise ValidationError('La votación no existe')