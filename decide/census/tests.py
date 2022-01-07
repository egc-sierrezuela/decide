import random
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient
from census import admin
from authentication.models import Persona
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

    def test_export_census_positive(self):
        #Test name: exportar_censo
        #Step # | name | target | value
        #1 | open | /admin/ | 
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

    def test_export_census_negative(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element_by_id('id_username').send_keys("adminprueba")
        self.driver.find_element_by_id('id_password').send_keys("qwerty",Keys.ENTER)

        
        # 2 | setWindowSize | 821x694 | 
        self.driver.set_window_size(821, 694)

        # 3 | click | linkText=Censuss | 
        self.driver.find_element(By.LINK_TEXT, "Censuss").click()

        # 4 | click | id=action-toggle | 
        #self.driver.find_element(By.ID, "action-toggle").click()

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

        #Si la exportación se ha realizado, debe aparecer un mensaje
        mensaje = self.driver.find_element(By.CLASS_NAME, "warning").text

        self.assertEquals(mensaje, 'Items must be selected in order to perform actions on them. No items have been changed.')

class ExportCensusUnitTest(BaseTestCase):

    def setUp(self):
        self.census = Census(voting_id = 1, voter_id=1)
        self.census.save()
        user_admin = User(username='admincensus', is_staff=True, is_superuser=True)
        user_admin.set_password=('qwerty')
        user_admin.save()
        self.user_admin = user_admin

        user_noadmin = User(username='simpleuser')
        user_noadmin.set_password('qwery')
        user_noadmin.save()
        self.user_noadmin = user_noadmin
        super().setUp()

    #Probamos que un usuario administrador exporta un censo y se lo descarga
    def test_export_census_positive(self):
        c = Client()
        c.force_login(self.user_admin)
        response = c.post("/admin/census/census/", {'action':'export_census', '_selected_action': str(self.census.id)}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename="censo.csv"')

    #Probamos que un usuario NO administrador intenta acceder al panel de administración y es redirigido al login
    def test_export_census_negative(self): 
        c = Client()
        c.force_login(self.user_noadmin)
        response = c.post("/admin/census/census/", {'action':'export_census', '_selected_action': str(self.census.id)}, format='json')
        self.assertEqual(response.status_code, 302)

class FilterCensusUnitTest(BaseTestCase):

    def setUp(self):

        #Creación de censos
        self.census = Census(voting_id = 1, voter_id=1)
        self.census.save()

        self.census2 = Census(voting_id = 1, voter_id=2)
        self.census2.save()

        self.census3 = Census(voting_id = 1, voter_id=3)
        self.census3.save()

        #Creación de usuarios que serán asociados a los censos
        user1 = User(id=1, username='simpleuser1')
        user1.set_password('qwerty')
        user1.save()

        user2 = User(id=2, username='simpleuser2')
        user2.set_password('qwerty')
        user2.save()

        user3 = User(id=3, username='simpleuser3')
        user3.set_password('qwerty')
        user3.save()

        #Creación de personas asociadas a censos
        pers1 = Persona(usuario=user1, sexo='masculino', ip= '127.0.0.1', region='ES', edad=18)
        pers1.save()

        pers2 = Persona(usuario=user2, sexo='femenino', ip= '127.0.0.1', region='ES', edad=41)
        pers2.save()

        pers3 = Persona(usuario=user3, sexo='otro', ip= '127.0.0.1', region='ES', edad=78)
        pers3.save()


        #Creación de usuario administrador
        user_admin = User(username='admincensus', is_staff=True, is_superuser=True)
        user_admin.set_password=('qwerty')
        user_admin.save()
        self.user_admin = user_admin
        super().setUp()

    def test_sex_filter_positive(self):
        filter = admin.SexCensusFilter(None, {'sexo':'hombre'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())[0]
        self.assertEqual(census.voter_id, 1)


        filter = admin.SexCensusFilter(None, {'sexo':'mujer'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())[0]
        self.assertEqual(census.voter_id, 2)

        filter = admin.SexCensusFilter(None, {'sexo':'otro'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())[0]
        self.assertEqual(census.voter_id, 3)

    def test_sex_filter_negative(self):
        filter = admin.SexCensusFilter(None, {'genero':'inventado'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())
        self.assertEqual(census, None)


    def test_age_filter_positive(self):
        filter = admin.AgeCensusFilter(None, {'edad':'18-30'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())[0]
        self.assertEqual(census.voter_id, 1)

        filter = admin.AgeCensusFilter(None, {'edad':'31-50'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())[0]
        self.assertEqual(census.voter_id, 2)

        filter = admin.AgeCensusFilter(None, {'edad':'50+'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())[0]
        self.assertEqual(census.voter_id, 3)

    
    def test_age_filter_negative(self):
        filter = admin.AgeCensusFilter(None, {'edad':'+75'}, Census, admin.CensusAdmin)
        census = filter.queryset(None, Census.objects.all())
        self.assertEqual(census, None)
    


    