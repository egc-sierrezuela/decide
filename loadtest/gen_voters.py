import json
import requests


HOST = "http://localhost:8000/"
USER = "decide"
PASS = "decide"


def create_voters(filename):
    """
    Create voters with requests library from filename.json, where key are
    usernames and values are the passwords.
    """
    with open(filename) as f:
        voters = json.loads(f.read())

    data = {'username': USER, 'password': PASS}
    response = requests.post(HOST + '/authentication/login/', data=data)
    token = response.json()

    voters_pk = []
    invalid_voters = []
    for username, pwd in voters.items():
        token.update({'username': username, 'password': pwd})
        response = requests.post(HOST + '/authentication/register/', data=token)
        if response.status_code == 201:
            voters_pk.append(response.json().get('user_pk'))
        else:
            invalid_voters.append(username)
    return voters_pk, invalid_voters

voters, invalids = create_voters('voters.json')
print("Create voters with pk={0} \nInvalid usernames={1}".format(voters, invalids))