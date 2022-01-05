from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from http import HTTPStatus
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase
from base.tests import BaseTestCase
from voting.models import Voting, Question, QuestionOption
from base import mods
from mixnet.models import Auth
from django.conf import settings

class VisualizerTestSelenium(LiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()

        user1=User(username='adminprueba')
        user1.set_password('qwerty')
        user1.is_superuser=True
        user1.save()
        
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def test_visualizer_voting_in_progress_sin_comenzar(self):
         voting = self.create_voting()
         self.driver.get(f'{self.live_server_url}/visualizer/'+str(voting.pk))

         self.assertEquals(
             self.driver.find_element_by_tag_name('h5').text,
             'Estado: Votación no comenzada.'
        )        

    def test_visualizer_voting_in_progress_comenzada(self):
        voting = self.create_voting()
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element_by_name('username').send_keys("adminprueba")
        self.driver.find_element_by_name('password').send_keys("qwerty")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(f'{self.live_server_url}/admin/voting/voting')

        self.driver.find_element_by_name('_selected_action').click()
        self.driver.find_element_by_xpath("//select[@name='action']/option[text()='Start']").click()
        self.driver.find_element_by_id("submit").click()

        self.assertEquals(
             self.driver.find_element_by_tag_name('h5').text,
             'Estado: Votación en progreso.'
        )

    def test_visualizer_voting_in_progress_finalizada(self):
        voting = self.create_voting()
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element_by_name('username').send_keys("adminprueba")
        self.driver.find_element_by_name('password').send_keys("qwerty")
        self.driver.find_element_by_id("submit").click()
        self.driver.implicitly_wait(100)
        self.driver.get(f'{self.live_server_url}/admin/voting/voting')

        self.driver.find_element_by_name('_selected_action').click()
        self.driver.find_element_by_xpath("//select[@name='action']/option[text()='Start']").click()
        self.driver.implicitly_wait(50)
        self.driver.find_element_by_xpath("//select[@name='action']/option[text()='Stop]").click()       

        self.driver.find_element_by_id("submit").click()

        self.assertEquals(
             self.driver.find_element_by_tag_name('h5').text,
             'Estado: Cerrada'
        )
