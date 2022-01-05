import random
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Census
from base import mods
from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    # def test_list_voting(self):
    #     # response = self.client.get('/census/?voting_id={}'.format(1), format='json')
    #     # self.assertEqual(response.status_code, 401)

    #     self.login(user='noadmin')
    #     response = self.client.get('/census/?voting_id={}'.format(1), format='json')
    #     self.assertEqual(response.status_code, 403)

    #     self.login()
    #     response = self.client.get('/census/?voting_id={}'.format(1), format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), {'voters': [1]})

    # def test_add_new_voters_conflict(self):
    #     data = {'voting_id': 1, 'voters': [1]}
    #     # response = self.client.post('/census/', data, format='json')
    #     # self.assertEqual(response.status_code, 401)

    #     self.login(user='noadmin')
    #     response = self.client.post('/census/', data, format='json')
    #     self.assertEqual(response.status_code, 403)

    #     self.login()
    #     response = self.client.post('/census/', data, format='json')
    #     self.assertEqual(response.status_code, 409)

    # def test_add_new_voters(self):
    #     data = {'voting_id': 2, 'voters': [1,2,3,4]}
    #     # response = self.client.post('/census/', data, format='json')
    #     # self.assertEqual(response.status_code, 401)

    #     self.login(user='noadmin')
    #     response = self.client.post('/census/', data, format='json')
    #     self.assertEqual(response.status_code, 403)

    #     self.login()
    #     response = self.client.post('/census/', data, format='json')
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

class ExportCensus(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.vars = {}
        self.census=Census(voting_id=1,voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_export_census(self):
        # Test name: exportar_censo
        # Step # | name | target | value
        # 1 | open | /admin/ | 
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element_by_id('id_username').send_keys("adminprueba")
        self.driver.find_element_by_id('id_password').send_keys("qwerty",Keys.ENTER)

        
        # 2 | setWindowSize | 821x694 | 
        self.driver.set_window_size(821, 694)

        # 3 | click | linkText=Censuss | 
        self.driver.find_element(By.LINK_TEXT, "Censuss").click()

        # 4 | click | id=action-toggle | 
        self.driver.find_element(By.ID, "action-toggle").click()

        # 5 | select | name=action | label=Export census
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Export census']").click()

        
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()

        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()

        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()

        # 6 | click | name=index | 
        self.driver.find_element(By.NAME, "index").click()

        #Refrescamos la página
        self.driver.refresh()

        #Si la exportación se ha realizado, debe aparecer un mensaje
        mensaje = self.driver.find_element(By.CLASS_NAME, "success").text

        self.assertEquals(mensaje, 'Exportación realizada con éxito')
