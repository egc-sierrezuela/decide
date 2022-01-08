from django.contrib.auth.models import User
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
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default="1")

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
        print("VOTES")
        print(votes)
        # anon votes
        return [[i['a'], i['b']] for i in votes]

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''
        #u=User.objects.all().filter(id=1)[0].auth_token
        votes = self.get_votes(token)

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

        self.do_postproc()


    def do_postproc(self):
        tally = self.tally
        points = self.points
        options = self.question.options.all()

        opts = []
        opciones = len(options)
        for opt in options:
            if isinstance(tally, list):
                if self.question.type != 2:
                    votes = tally.count(opt.number)
                else:
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
 
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'points': points,
                'votes': votes
            })

        data = { 'type': self.question.type, 'options': opts ,'tally':tally}
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
