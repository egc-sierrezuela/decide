from rest_framework.views import APIView
from rest_framework.response import Response


class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            })

        out.sort(key=lambda x: -x['postproc'])
        return out

      
    def equality(self, options):
        out = []
        n_women = 0
        n_men = 0
        rel = 0.
        is_men_greater = False

        for opt in options:
            n_women += sum(opt['votes_fem'])
            n_men += sum(opt['votes_masc'])

        if n_women > n_men:
            rel = n_men/n_women
        else:
            rel = n_women/n_men
            is_men_greater = True

        for opt in options:
            votes = 0
            if is_men_greater:
                votes = sum(opt['votes_fem']) + sum(opt['votes_masc'])*rel
            else:
                votes = sum(opt['votes_masc'])+ sum(opt['votes_fem'])*rel

            out.append({
                **opt,
                'postproc': round(votes),
            })

        out.sort(key=lambda x: -x['postproc'])
        return out

      
    def borda(self, options):
        out = []

        for opt in options:
            votos = 0
            preference = 0
            #Numero total de votos por questions para ordenar por preferencia
            n = len(opt['votes'])        
            while preference < n:
                #Preference es una variable que indica el orden de preferencia de las respuestas a las questions de las votaciones
                votos += (n-preference)* opt['votes'][preference]
                preference +=1
            out.append({
                    **opt,
                    'postproc': votos,
                })

        out.sort(key=lambda x: -x['postproc'])
        return out


    def proportional_representation(self, options, type): #EGC-GUADALENTIN
        out = []
        votes = []
        points_for_opt = []
        #Sainte Lague reparte los escaños de forma más equitativa, penalizando en mayor medida mientras más escaños tenga una opción
        multiplier = 2 if type == 'SAINTE_LAGUE' else 1
        points = options[0]['points']
        zero_votes = True

        for i in range(0, len(options)):
            votes.append(options[i]['votes'])
            points_for_opt.append(0)
            if zero_votes is True and options[i]['votes'] != 0:
                zero_votes = False

        if zero_votes is False:
            for i in range(0, points):
                max_index = votes.index(max(votes))
                points_for_opt[max_index] += 1
                votes[max_index] = options[max_index]['votes'] / (multiplier * points_for_opt[max_index] + 1)

        for i in range(0, len(options)):
            out.append({
                **options[i],
                'postproc': points_for_opt[i],
            })

        out.sort(key=lambda x: (-x['postproc'], -x['votes']))
        return out

      
    def post(self, request):

        """
         * type: IDENTITY | EQUALITY | WEIGHT
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]

        * type: EQUALITY
        * options: [
            {
             option: str,
             number: int,
             votes_men: int,
             votes_women: int,
            }
           ]
        """

        out = []
        questions = request.data

        result = None
        t = questions['type']
        opts = questions['options']

        if t == 0:
            result = self.identity(opts)
        if t == 2:
            result = self.borda(opts)
        if t == 4:
            result = self.equality(opts)
        if t == 3 or t == 1:
            result = self.proportional_representation(opts, t)
                
        out.append({'type': t, 'options': result})

        return Response(out)
