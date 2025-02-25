from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from http import HTTPStatus
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase
from base.tests import BaseTestCase
from selenium.webdriver.support.ui import Select

from base import mods


class AuthTestSelenium(LiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

        u2 = User(username='pepe')
        u2.set_password('pepe')
        u2.email="pepe@a.a"
        u2.save()

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()


    def test_simpleCorrectLogin(self):     
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')               
        self.driver.get(f'{self.live_server_url}/authentication/login-alt/')
        self.driver.find_element_by_id('id_username').send_keys("pepe")
        self.driver.find_element_by_id('id_password').send_keys("pepe",Keys.ENTER)
        
        
        print(self.driver.current_url)
        #Comprueba si redirige a la url correcta al loguearse correctamente
        self.assertTrue(self.driver.current_url==f'{self.live_server_url}/authentication/login-success/')

    def test_incorrectLoginUserNotExist(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')               
        self.driver.get(f'{self.live_server_url}/authentication/login-alt/')
        self.driver.find_element_by_id('id_username').send_keys("UsuarioNoExistente")
        self.driver.find_element_by_id('id_password').send_keys("UsuarioNoExistente",Keys.ENTER)

        text = "Error: Usuario o contraseña incorrectas."
        assert (text in self.driver.page_source)

    def test_incorrectLoginPassIncorrect(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')               
        self.driver.get(f'{self.live_server_url}/authentication/login-alt/')
        self.driver.find_element_by_id('id_username').send_keys("pepe")
        self.driver.find_element_by_id('id_password').send_keys("ContraseñaIncorrecta",Keys.ENTER)

        text = "Error: Usuario o contraseña incorrectas."
        assert (text in self.driver.page_source)

    def test_register(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')               
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')
        
    
        
        self.driver.find_element_by_id('id_username').send_keys("pepe1")
        self.driver.find_element_by_id('id_email').send_keys("compaferdebuggeaconerroresdeldecide@a.a")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("contraseña",Keys.ENTER)

        #self.driver.find_element_by_class_name('btn').click()
        
        # Comprueba si redirige a la url correcta al loguearse correctamente
        self.driver.implicitly_wait(2)
        self.assertTrue(self.driver.current_url==f'{self.live_server_url}/authentication/login-success/')
        
        # Comprueba que el mensaje es el correcto
        text = "Has iniciado sesion con exito. Bienvenido, pepe1."
        assert (text in self.driver.page_source)

    
    def test_incorretRegisterUserAlreadyRegistered(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')               
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')
        
        self.driver.find_element_by_id('id_username').send_keys("admin") # Ya existente en la base de datos
        self.driver.find_element_by_id('id_email').send_keys("admin@a.a")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("contraseña",Keys.ENTER)

        
        # Comprueba que el mensaje es el correcto
        text = "Error: Usuario ya existente."
        assert (text in self.driver.page_source)

    def test_incorretRegisterEmailAlreadyRegistered(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')               
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')
        
        self.driver.find_element_by_id('id_username').send_keys("antonio") 
        self.driver.find_element_by_id('id_email').send_keys("pepe@a.a") # Ya existente en la base de datos
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("contraseña",Keys.ENTER)

        
        # Comprueba que el mensaje es el correcto
        text = "Email exists"
        assert (text in self.driver.page_source) 

    def test_incorretRegisterEmailBadFormat1(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')

        self.driver.find_element_by_id('id_username').send_keys("antonio") 
        self.driver.find_element_by_id('id_email').send_keys("a")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("contraseña",Keys.ENTER)


        # Comprueba que el mensaje es el correcto

        self.driver.implicitly_wait(10)

        email_input = self.driver.find_element_by_id('id_email')
        validation_message = email_input.get_attribute("validationMessage")

        alert = 'Incluye un signo "@" en la dirección de correo electrónico. La dirección "a" no incluye el signo "@".'
        assert (alert==validation_message)

    def test_incorretRegisterEmailBadFormat2(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')

        self.driver.find_element_by_id('id_username').send_keys("antonio") 
        self.driver.find_element_by_id('id_email').send_keys("a@")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("",Keys.ENTER)


        # Comprueba que el mensaje es el correcto

        self.driver.implicitly_wait(10)

        email_input = self.driver.find_element_by_id('id_email')
        validation_message = email_input.get_attribute("validationMessage")

        alert = 'Introduce texto detrás del signo "a". La dirección "a@" está incompleta.'
        assert (alert==validation_message)          

    def test_incorretRegisterEmailBadFormat2(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')

        self.driver.find_element_by_id('id_username').send_keys("antonio") 
        self.driver.find_element_by_id('id_email').send_keys("a@.")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("",Keys.ENTER)


        # Comprueba que el mensaje es el correcto

        self.driver.implicitly_wait(10)

        email_input = self.driver.find_element_by_id('id_email')
        validation_message = email_input.get_attribute("validationMessage")

        alert = 'El signo "." está colocado en una posición incorrecta en la dirección ".".'
        assert (alert==validation_message)          

    def test_incorretRegisterUserEmpty(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')

        self.driver.find_element_by_id('id_username').send_keys("") 
        self.driver.find_element_by_id('id_email').send_keys("a")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("contraseña",Keys.ENTER)


        # Comprueba que el mensaje es el correcto

        self.driver.implicitly_wait(10)

        user_input = self.driver.find_element_by_id('id_username')
        validation_message = user_input.get_attribute("validationMessage")

        alert = 'Completa este campo'
        assert (alert==validation_message)            

    def test_incorretRegisterEmailEmpty(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')

        self.driver.find_element_by_id('id_username').send_keys("antonio") 
        self.driver.find_element_by_id('id_email').send_keys("")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("contraseña",Keys.ENTER)


        # Comprueba que el mensaje es el correcto

        self.driver.implicitly_wait(10)

        email_input = self.driver.find_element_by_id('id_email')
        validation_message = email_input.get_attribute("validationMessage")

        alert = 'Completa este campo'
        assert (alert==validation_message)


    def test_incorretRegisterPasswordEmpty(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')

        self.driver.find_element_by_id('id_username').send_keys("antonio") 
        self.driver.find_element_by_id('id_email').send_keys("pepe@gmail.com")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("12")
        self.driver.find_element_by_id('id_password').send_keys("",Keys.ENTER)


        # Comprueba que el mensaje es el correcto

        self.driver.implicitly_wait(10)

        pass_input = self.driver.find_element_by_id('id_password')
        validation_message = pass_input.get_attribute("validationMessage")

        alert = 'Completa este campo'
        assert (alert==validation_message)   

    def test_incorretRegisterAgeEmpty(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')
        self.driver.get(f'{self.live_server_url}/authentication/register-alt/')

        self.driver.find_element_by_id('id_username').send_keys("antonio") 
        self.driver.find_element_by_id('id_email').send_keys("pepe@gmail.com")
        Select(self.driver.find_element_by_id('id_sexo')).select_by_visible_text('Hombre')
        self.driver.find_element_by_id('id_edad').send_keys("")
        self.driver.find_element_by_id('id_password').send_keys("contraseña",Keys.ENTER)


        # Comprueba que el mensaje es el correcto

        self.driver.implicitly_wait(10)

        edad_input = self.driver.find_element_by_id('id_edad')
        validation_message = edad_input.get_attribute("validationMessage")

        alert = 'Completa este campo'
        assert (alert==validation_message)
