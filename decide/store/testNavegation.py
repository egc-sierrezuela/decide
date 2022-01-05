from django.test import TestCase
from census.models import Census
from base.models import Auth
from voting.models import Question, Voting
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from http import HTTPStatus
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from authentication.forms import RegisterForm
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
from authentication.models import Persona

from base import mods

class StoreTestSelenium(LiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

        u1 = User(username='pepe')
        u1.set_password('pepe')
        u1.email="pepe@a.a"
        u1.is_superuser=True
        u1.save()

        p1 = Persona()
        p1.usuario=u1
        p1.sexo="hombre"
        p1.ip="121.12.1.1"
        p1.region="ES"
        p1.edad=23
        p1.save()

        q1 = Question()
        q1.desc = "kll"
        q1.save()

        v1 = Voting()
        v1.pk=1
        v1.question=q1
        v1.name = "Prueba"
        v1.save()
   
        c1=Census(voting_id=v1.id,voter_id=u1.id)
        c1.save()

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_VisualizerCorrectPanelTitulo(self):
        self.driver.get(f'{self.live_server_url}/authentication/logout-alt/')               
        self.driver.get(f'{self.live_server_url}/authentication/login-alt/')
        self.driver.find_element_by_id('id_username').send_keys("pepe")
        self.driver.find_element_by_id('id_password').send_keys("pepe",Keys.ENTER)

        self.driver.get(f'{self.live_server_url}/store/1/')
        self.assertTrue(self.driver.current_url==f'{self.live_server_url}/store/1/')

        text = "Usuarios de la votacion 1 :"
        assert (text in self.driver.page_source)


    

