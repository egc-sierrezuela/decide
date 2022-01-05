from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
import urllib

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
    question = models.ManyToManyField(Question, related_name='voting')

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
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
        return votes

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes  = self.get_votes(token)
        votos = []
        for i in votes:
            if type(i)=='dict':
                aa=i['a'].replace("[","").replace("]","").replace("'","").replace(" ","").split(",")
                bb=i['b'].replace("[","").replace("]","").replace("'","").replace(" ","").split(",")
                for j in range(0,len(aa)):
                    votos.append([int(aa[j]), int(bb[j]), j])

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votos }
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
        return tally


    def do_postproc(self):
        tally = self.tally
        tallies = ['IDENTITY', 'BORDA', 'HONDT', 'EQUALITY', 'SAINTE_LAGUE']
        data = []

        for i, q in enumerate(self.question.all()):
            opciones = q.options.all()
            opt_count=len(opciones)
            opts = []
            for opt in opciones:
                votes = 0
                for dicc in tally:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos!=None and pos[1]==q.id:
                        votes = votes + 1
                opts.append({
                    'question': opt.question.desc,
                    'question_id':opt.question.id,
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })
            data.append( { 'type': tallies[q.type],'options': opts})
        postp = mods.post('postproc', json=data)
        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
