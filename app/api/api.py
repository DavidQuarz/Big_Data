import requests
import json

### Obtenir le token ###

def get_token():
	urlOAuth = 'https://as.api.iledefrance-mobilites.fr/api/oauth/token'
	client_id='4c2c5433-85da-4961-a836-d05bccdbc769'
	client_secret='506a0fc0-f369-4106-8138-1f47cc55b50b'

	data =dict(
		grant_type='client_credentials',
		scope='read-data',
		client_id=client_id,
		client_secret=client_secret
		)

	response = requests.post(urlOAuth, data=data)
	print(response.json)

	if response.status_code != 200:
		print('Status:', response.status_code, 'Erreur sur la requête; fin de programme')
		exit()

	jsonData = response.json()
	token = jsonData['access_token']
	
	return token


### Requêter l'API ###
def request_api():
	url = 'https://traffic.api.iledefrance-mobilites.fr/v1/tr-unitaire/stop-monitoring'
	params =dict(MonitoringRef='STIF:StopPoint:Q:411414:')
	headers = {
		'Accept-Encoding' : 'gzip',
		'Authorization' : 'Bearer ' + get_token()
		}
	response = requests.get(url, params=params, headers=headers)

	if response.status_code != 200:
		print('Status:', response.status_code, 'Erreur sur la requête; fin de programme')
		exit()

	jsonData = response.json()

	with open('./app/api/stop/stop_saint_denis.json', 'w') as outfile:
		json.dump(jsonData, outfile, indent = 4)
