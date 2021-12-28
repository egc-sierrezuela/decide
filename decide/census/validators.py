from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validation_census_voter_id(value):
    voters_exitentes=User.objects.all()
    ids=[]
    for i in range(0,len(voters_exitentes)):
        ids.append(int(voters_exitentes[i].id))
    if value not in ids:
        raise ValidationError('El/La votante no existe')
    