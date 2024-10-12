from datetime import datetime
import multiprocessing
import multiprocessing.process
import facebook
import requests
import time

FacebookToken = "FACEBOOKTOKEN"
pageID = "PAGEID"
InstagramID = "INSTAGRAMID"
CountyCode = "COUNTYCODE"
ForecastCode = "FORECASTCODE"
RadarImageURL = "RADARIMAGEURL"
ActiveWeatherAlerts = []
LastRecordedWeatherSent = datetime.now().day-1
if(LastRecordedWeatherSent == 0):
    LastRecordedWeatherSent = 28
LastRecordedWeatherSent = datetime(1,1,LastRecordedWeatherSent)

# Initialize the Graph API
graph = facebook.GraphAPI(FacebookToken)

def PostToInstagram(Message, ImageURl):
    try:
        create_media_url = f"https://graph.facebook.com/v20.0/{InstagramID}/media"
        media_params = {
            'image_url': ImageURl,
            'caption': Message,
            'access_token': FacebookToken
        }
        media_response = requests.post(create_media_url, params=media_params)

        if media_response.status_code == 200:
            media_id = media_response.json().get('id')
            if media_id:
                print("Media container created with ID:", media_id)

                # Step 2: Publish the media container
                publish_url = f"https://graph.facebook.com/v20.0/{InstagramID}/media_publish"
                publish_params = {
                    'creation_id': media_id,
                    'access_token': FacebookToken
                }
                publish_response = requests.post(publish_url, params=publish_params)
                if publish_response.status_code == 200:
                    print("posted successfully on Instagram!")
                else:
                    # Error handling with details from the response
                    error_details = publish_response.json().get('error', {})
                    print(f"Error in publishing: {error_details.get('message', 'Unknown error')}")
            else:
                print("Failed to retrieve media container ID.")
        else:
            # Error handling with details from the response
            error_details = media_response.json().get('error', {})
            print(f"Error in media creation: {error_details.get('message', 'Unknown error')}, Code: {error_details.get('code', 'N/A')}, Type: {error_details.get('type', 'N/A')}")
    except:
        print("Error Occured")

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