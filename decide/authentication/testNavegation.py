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