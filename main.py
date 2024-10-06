from datetime import datetime
import multiprocessing
import multiprocessing.process
import facebook
import requests
import time

FacebookToken = "FACEBOOKTOKEN"
pageID = "PAGEID"
CountyCode = "COUNTYCODE"
ForecastCode = "FORECASTCODE"
ActiveWeatherAlerts = []
LastRecordedWeatherSent = datetime.now().day-1
if(LastRecordedWeatherSent == 0):
    LastRecordedWeatherSent = 28
LastRecordedWeatherSent = datetime(1,1,LastRecordedWeatherSent)

# Initialize the Graph API
graph = facebook.GraphAPI(FacebookToken)

# Post the message to the page feed
def PostToFacebook(Message):
    try:
        response = graph.put_object(pageID, 'feed', message=Message)
        print('Post ID:', response['id'])
        return response['id']
    except facebook.GraphAPIError as e:
        print('An error occurred:', e)

def EditFacebookPost(MessageID, Message):
    try:
        response = graph.put_object(parent_object=MessageID, connection_name='', message=Message)
        print('Post was edited.')
    except facebook.GraphAPIError as e:
        print('An error occurred:', e)

def GetWeather():
    weather = requests.get(f"https://api.weather.gov/zones/forecast/{ForecastCode}/forecast")
    if weather.status_code == 200:
        print("Request was successful!")
        return weather.json()
    else:
        print(f"Request failed with status code: {weather.status_code}")
        time.sleep(10)
        return GetWeather()

def GetAlerts():
    try:
        alerts = requests.get(f"https://api.weather.gov/alerts/active/zone/{CountyCode}")
        if alerts.status_code == 200:
            print("Request was successful!")
            return alerts.json()['features']
        else:
            print(f"Request failed with status code: {alerts.status_code}")
            return ActiveWeatherAlerts
    except:
        print('Error occured')
        return ActiveWeatherAlerts

def MainAlerts():
    while True:
        print(ActiveWeatherAlerts)
        Alerts = GetAlerts()
        if Alerts:
            for alert in Alerts:
                if not alert['id'] in [item[0] for item in ActiveWeatherAlerts]:
                    print("New Alert")
                    date = datetime.fromisoformat(alert['properties']['sent'])
                    PostText = ""
                    if(not alert['properties']['parameters']['NWSheadline'] in ["", "null", None]):
                        PostText+=f"{alert['properties']['parameters']['NWSheadline'][0]}\n"
                    else:
                        PostText+=f"{alert['properties']['event']}\n"

                    PostText += f"{alert['properties']['headline']}\n\nSeverity\n{alert['properties']['severity']}"

                    if not alert['properties']['certainty'] in ["", "null", None]:
                        PostText+=f"\n\nCertainty\n{alert['properties']['certainty']}"

                    PostText+=f"\n\nDescription\n{alert['properties']['description']}"

                    if not alert['properties']['instruction'] in ["", "null", None]:
                        PostText+=f"\n\nInstruction\n{alert['properties']['instruction']}"

                    postID = PostToFacebook(PostText)
                    ActiveWeatherAlerts.append([alert['id'], postID, PostText])
            else:
                print("No New Alert")
        else:
            print("No Active Alerts")
        
        alertsToDelete = []
        for index,alert in enumerate(ActiveWeatherAlerts):
            if not alert[0] in [item['id'] for item in Alerts]:
                EditFacebookPost(alert[1], f"Expired\n{alert[2]}")
                print("Alert Expired")
                alertsToDelete.append(index)

        for values in range(0, len(alertsToDelete)):
            index = len(alertsToDelete) - (values+1)
            ActiveWeatherAlerts.pop(index)
            
        time.sleep(5)

    


def MainWeather():
    global LastRecordedWeatherSent
    while True:
        time.sleep(1)
        if datetime.now().hour == 6 and datetime.now().day != LastRecordedWeatherSent.day:
            LastRecordedWeatherSent = datetime.now()
            LastRecordedWeatherSent = LastRecordedWeatherSent.replace(hour=6, minute=0, second=0, microsecond=0)
            weather = GetWeather()
            today = weather['properties']['periods'][0]
            tonight = weather['properties']['periods'][1]
            PostText = f"{today['name']}\n{today['detailedForecast']}\n\n{tonight['name']}\n{tonight['detailedForecast']}"
            PostToFacebook(PostText)

def Main():
    WeatherProcess = multiprocessing.Process(target=MainWeather)
    AlertProcess = multiprocessing.Process(target=MainAlerts)

    WeatherProcess.start()
    AlertProcess.start()

    WeatherProcess.join()
    AlertProcess.join()


if __name__ == "__main__":
    Main()