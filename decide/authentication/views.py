from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView, View
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from django.db import IntegrityError
from django.shortcuts import get_object_or_404,render,redirect
from django.core.exceptions import ObjectDoesNotExist
from authentication.forms import RegisterForm
from django.http import HttpResponse

from .serializers import UserSerializer


class GetUserViewAPI(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutViewAPI(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterViewAPI(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)


class RegisterView(View):

    def get(get, request):
        if(not request.user.is_authenticated):
            form = RegisterForm()
            params = {'form':form}
            return render(request,'register.html',params)
        else:
            return HttpResponse('Debe ingresar como usuario anonimo',status=401)
        
    def post(self, request):
        form = RegisterForm(request.POST)
        if not form.is_valid():
            params = {'form':form}
            return render(request,'register.html',params)
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        pwd = form.cleaned_data['password']
        try:
            user = User(username=username)
            user.email = email
            user.set_password(pwd)
            user.save()
            login(request,user)
        except IntegrityError:
            params = {'form':form, 'message':'Usuario ya existente.'}
            return render(request,'register.html',params)
        params = {'username':username}
        return render(request,'succesful_register.html',params)

