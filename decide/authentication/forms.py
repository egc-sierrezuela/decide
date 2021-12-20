# -*- encoding: utf-8 -*-
from django import forms
from captcha.fields import ReCaptchaField

class RegisterForm(forms.Form):
    username = forms.CharField(label='Usuario',widget=forms.TextInput,required=True)
    email = forms.CharField(label='Email',widget=forms.EmailInput,required=True)
    password = forms.CharField(label='Contraseña',widget=forms.PasswordInput,required=True)
    captcha = ReCaptchaField()