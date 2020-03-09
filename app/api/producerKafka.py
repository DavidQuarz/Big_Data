import requests, json, time
from kafka import KafkaProducer
def get_access_token():
  urlOAuth= 'https://as.api.iledefrance-mobilites.fr/api/oauth/token'
  client_id='342fe700-3f5c-417b-a36d-14b063461ecd'
  client_secret='58032e87-8a3c-4d52-ac68-607dbca615e2'
  data =dict(grant_type='client_credentials' , scope='read-data',client_id=client_id,client_secret=client_secret)
  response= requests.post(urlOAuth, data=data, verify=False)

  if(response.status_code != 200):
    print('Status: ', response.status_code ,'Erreur sur la requete; fin de programme')
    exit()
  jsonData= response.json()
  return jsonData['access_token']

def getStationData(idStation,defaultToken):
 URL="https://traffic.api.iledefrance-mobilites.fr/v1/tr-unitaire/stop-monitoring"
 PARAMS={}
 headerParams={}
 PARAMS["MonitoringRef"]=idStation
 headerParams["Authorization"]= "Bearer "+ defaultToken
 response=requests.get(URL,params=PARAMS, headers=headerParams)
 return response

producer = KafkaProducer(bootstrap_servers="localhost:9092")
defaultToken=get_access_token()
arrets=["STIF:StopPoint:Q:41123:","STIF:StopPoint:Q:41107:","STIF:StopPoint:Q:41111:","STIF:StopPoint:Q:41113:","STIF:StopPoint:Q:41104:","STIF:StopPoint:Q:411423:","STIF:StopPoint:Q:41118:","STIF:StopPoint:Q:41089:","STIF:StopPoint:Q:41103:","STIF:StopPoint:Q:411331:","STIF:StopPoint:Q:41092:","STIF:StopPoint:Q:41078:","STIF:StopPoint:Q:41110:","STIF:StopPoint:Q:411415:","STIF:StopPoint:Q:411425:","STIF:StopPoint:Q:41084:","STIF:StopPoint:Q:41086:","STIF:StopPoint:Q:411325:","STIF:StopPoint:Q:41122:","STIF:StopPoint:Q:41094:","STIF:StopPoint:Q:41112:","STIF:StopPoint:Q:411414:","STIF:StopPoint:Q:41083:","STIF:StopPoint:Q:41085:","STIF:StopPoint:Q:41116:","STIF:StopPoint:Q:41119:","STIF:StopPoint:Q:41102:","STIF:StopPoint:Q:41120:","STIF:StopPoint:Q:41121:","STIF:StopPoint:Q:41074:","STIF:StopPoint:Q:411424:","STIF:StopPoint:Q:41087:","STIF:StopPoint:Q:41129:","STIF:StopPoint:Q:41106:","STIF:StopPoint:Q:41090:","STIF:StopPoint:Q:41091:","STIF:StopPoint:Q:41124:","STIF:StopPoint:Q:41108:","STIF:StopPoint:Q:41114:","STIF:StopPoint:Q:41071:","STIF:StopPoint:Q:41093:","STIF:StopPoint:Q:41115:","STIF:StopPoint:Q:41079:","STIF:StopPoint:Q:41125:","STIF:StopPoint:Q:41109:","STIF:StopPoint:Q:41105:","STIF:StopPoint:Q:41117:","STIF:StopPoint:Q:41088:","STIF:StopPoint:Q:411328:","STIF:StopPoint:Q:411439:"]
while True:
  for arret in arrets:
    response=getStationData(arret,defaultToken)
    if(response.status_code==401):
      defaultToken=get_access_token()
      response=getStationData(idStation)
    data=response.json()
    producer.send("RealTime-Transilien-Topic", json.dumps(data))
  time.sleep(1)
      
