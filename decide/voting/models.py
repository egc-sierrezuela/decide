from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
import urllib
from authentication.models import Persona
from base import mods
from base.models import Auth, Key


class Question(models.Model):
    desc = models.TextField()
    type=models.IntegerField(choices={(0, "IDENTITY"),(1,'DHONT'),(2,'BORDA'),(3,'SAINTE_LAGUE'),(4, "EQUALITY")},default=1)

    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default="1")

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    tallyM = JSONField(blank=True, null=True)
    tallyH = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    url = models.URLField(help_text=u"http://localhost:8000/booth/")

    def clean_fields(self, exclude=None):
        super(Voting, self).clean_fields(exclude)
        
        url = urllib.parse.quote_plus(self.url.encode('utf-8'))
        
        print(Voting.objects.filter(url=url))


    def save(self, *args, **kwargs):
        try:
            Voting.objects.get(name=self.name)
        except:
            encode_url = urllib.parse.quote_plus(self.url.encode('utf-8'))
            self.url = encode_url
            
        super(Voting, self).save(*args, **kwargs)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return [[i['a'], i['b']] for i in votes]
    
    def get_votes_equality(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return votes

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''
        u=User.objects.all().filter(id=1)[0].auth_token
        votes = self.get_votes(str(u))

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        tally=self.tally
        self.tally_votes_H(str(u))

        return tally

    def tally_votes_H(self, token):
        '''
        The tally is a shuffle and then a decrypt
        '''
        votos = self.get_votes_equality(token)
        votes_aux = []
        for i in votos:
            votanteP=Persona.objects.all().filter(id=i['voter_id'])[0]
            if votanteP.sexo == 'hombre':
                votes_aux.append(i)

        votes=[[i['a'], i['b']] for i in votes_aux]

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tallyH = response.json()
        self.save()

        tallyH=self.tallyH

        self.tally_votes_M(token)
        return tallyH
    

    def tally_votes_M(self, token):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votos = self.get_votes_equality(token)
        votes_aux = []
        for i in votos:
            votanteP=Persona.objects.all().filter(id=i['voter_id'])[0]
            if votanteP.sexo == 'mujer':
                votes_aux.append(i)

        votes=[[i['a'], i['b']] for i in votes_aux]

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tallyM = response.json()
        self.save()

        tallyM=self.tallyM
        self.do_postproc()
        return tallyM
    


    def do_postproc(self):
        tally = self.tally
        tallyM=self.tallyM
        tallyH=self.tallyH
        points = self.points
        options = self.question.options.all()
        opts = []
        opciones = len(options)
        for opt in options:
            if isinstance(tally, list):
                if self.question.type != 2 and self.question.type!=4:
                    votes = tally.count(opt.number)
                    votesH = 0
                    votesM = 0
                elif self.question.type == 4:
                    votes = []
                    votesM = []
                    votesH = []
                    for i in range(opciones):
                        votes.append(0)
                        votesM.append(0)
                        votesH.append(0)

                    for pos in tally:
                        if pos!=None and pos==opt.number:
                            votes[pos-1] = votes[pos-1] + 1
                    for pos in tallyM:
                        if pos!=None and pos==opt.number:
                            votesM[pos-1] = votesM[pos-1] + 1
                    for pos in tallyH:
                        if pos!=None and pos==opt.number:
                            votesH[pos-1] = votesH[pos-1] + 1
                else:
                    votesH = 0
                    votesM = 0
                    votes = []
                    i = 0
                    while i < opciones:
                        votes.append(0)
                        i+=1
                    for vote in tally:
                        o = 0
                        vot = str(vote)
                        while o < len(vot):
                            if vot[o] == str(opt.number):
                                votes[o] +=1
                            o+=1
            else:
                votes = 0
                votesH = 0
                votesM = 0
 
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'points': points,
                'votes': votes,
                'votes_masc': votesH,
                'votes_fem': votesM,
            })

        data = { 'type': self.question.type, 'options': opts}
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
