from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods


class PostProcTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        self.client = None


    def test_identity(self):
        data = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5},
                {'option': 'Option 2', 'number': 2, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'votes': 3},
                {'option': 'Option 4', 'number': 4, 'votes': 2},
                {'option': 'Option 5', 'number': 5, 'votes': 5},
                {'option': 'Option 6', 'number': 6, 'votes': 1},
            ]
        }]

        expected_result = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 5', 'number': 5, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 3', 'number': 3, 'votes': 3,
                 'postproc': 3},
                {'option': 'Option 4', 'number': 4, 'votes': 2,
                 'postproc': 2},
                {'option': 'Option 6', 'number': 6, 'votes': 1,
                 'postproc': 1},
                {'option': 'Option 2', 'number': 2, 'votes': 0,
                 'postproc': 0},
            ]
        }]

        print("VALUE:")
        print(data)
        print("EXPECTED_VALUE:")
        print(expected_result)

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)



    #TEST PARA MULTIPLES PREGUNTAS--De Guadalentin
    def test_identity_multiple_questions(self):
        data = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5},
                {'option': 'Option 2', 'number': 2, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'votes': 3}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 2},
                {'option': 'Option 2', 'number': 2, 'votes': 5},
                {'option': 'Option 3', 'number': 3, 'votes': 1}
            ]
        }]

        #El orden debe ser descendente, según el serializer
        expected_result = [{
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 3', 'number': 3, 'votes': 3,
                 'postproc': 3},
                {'option': 'Option 2', 'number': 2, 'votes': 0,
                 'postproc': 0}
            ]
        }, {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 2', 'number': 2, 'votes': 5,
                 'postproc': 5},
                {'option': 'Option 1', 'number': 1, 'votes': 2,
                 'postproc': 2},
                {'option': 'Option 3', 'number': 3, 'votes': 1,
                 'postproc': 1}
            ]
        }]

        print("VALUE:")
        print(data)
        print("EXPECTED_VALUE:")
        print(expected_result)

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)