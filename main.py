from datetime import datetime
from datetime import date
import multiprocessing
import multiprocessing.process
import facebook
import requests
import time
import os


#Facebook/Instagram
FacebookToken = "FacebookToken"
pageID = "PageID"
InstagramID = "InstagramID"
CountyName = "CountyName"
CountyCode = "CountyCode"
ForecastCode = "ForecastCode"
RadarImageURL = "RadarImage"

#Threads
ThreadsToken = "ThreadsToken"
ThreadsID = "ThreadsID"

#Paths
DiscordQueue = r"PATH"

ActiveWeatherAlerts = []
LastRecordedAlertData = ''
LastRecordedWeatherSent = datetime.now().day-1
if(LastRecordedWeatherSent == 0):
    LastRecordedWeatherSent = 28
LastRecordedWeatherSent = datetime(1,1,LastRecordedWeatherSent)

graph = facebook.GraphAPI(FacebookToken)

def PostToInstagram(Message, ImageURl):
    try:
        media_params = {
            'image_url': ImageURl,
            'caption': Message,
            'access_token': FacebookToken
        }
        media_response = requests.post(f"https://graph.facebook.com/v20.0/{InstagramID}/media", params=media_params)

        if media_response.status_code == 200:
            media = media_response.json()
            if "id" in media:
                print("Media container created with ID:", media['id'])
                publish_params = {
                    'creation_id': media['id'],
                    'access_token': FacebookToken
                }
                publish_response = requests.post(f"https://graph.facebook.com/v20.0/{InstagramID}/media_publish", params=publish_params)
                if publish_response.status_code == 200:
                    print("posted successfully on Instagram!")
                else:
                    error_details = publish_response.json().get('error', {})
                    print(f"Error in publishing: {error_details.get('message', 'Unknown error')}")
            else:
                print("Media didn't return ID.")
        else:
            error_details = media_response.json().get('error', {})
            print(f"Error in media creation: {error_details.get('message', 'Unknown error')}, Code: {error_details.get('code', 'N/A')}, Type: {error_details.get('type', 'N/A')}")
    except:
        print("Error Occured")

def PostToThreads(Message):
    try:
        ThreadsPostData = {
            'text':Message,
            'media_type': 'TEXT',
            'access_token': ThreadsToken
        }

        MediaRequest = requests.post(f"https://graph.threads.net/v1.0/{ThreadsID}/threads", params=ThreadsPostData)
        if(MediaRequest.status_code == 200):
            media = MediaRequest.json()

            if("id" in media):
                print("Media container created with ID:", media['id'])
                PostParams = {
                    'creation_id':media['id'],
                    'access_token':ThreadsToken
                }
                PostRequest = requests.post(f"https://graph.threads.net/v1.0/{ThreadsID}/threads_publish", params=PostParams)
                if(PostRequest.status_code == 200):
                    print("posted successfully on Threads!")
                else:
                    print(f"error {PostRequest.status_code} occured ")

            else:
                print("Media didn't return Id")
            
        else:
            print(f"error {MediaRequest.status_code} occured media")

    except:
        print("Error Occured")

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
            global LastRecordedAlertData
            LastRecordedAlertData = alerts.json()['features']
            return alerts.json()['features']
        else:
            print(f"Request failed with status code: {alerts.status_code}")
            return LastRecordedAlertData
    except:
        print('Error occured')
        return LastRecordedAlertData

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
                    ThreadsPostText = ""
                    DiscordEmbed = {"Type":"Alert", "County":CountyName}
                    if(not alert['properties']['parameters']['NWSheadline'] in ["", "null", None]):
                        NWSHeadline = f"{alert['properties']['parameters']['NWSheadline'][0]}"
                        PostText+=f"{NWSHeadline}\n"
                        ThreadsPostText+=f"{NWSHeadline}\n"
                        DiscordEmbed["Title"] = f"{CountyName} County {NWSHeadline}"

                    else:
                        Event = f"{alert['properties']['event']}\n"
                        PostText+=f"{Event}\n"
                        ThreadsPostText+=f"{Event}\n"
                        DiscordEmbed["Title"] = f"{CountyName} County {Event}"

                    PostText += f"{alert['properties']['headline']}\n\nSeverity\n{alert['properties']['severity']}"
                    ThreadsPostText+=f"{alert['properties']['headline']}\n\nSeverity\n{alert['properties']['severity']}"
                    DiscordEmbed["Headline"] = alert['properties']['headline']
                    DiscordEmbed["Severity"] = alert['properties']['severity']

                    FixedID = str(alert['id']).replace("https://api.weather.gov/alerts/", "")
                    ThreadsPostText+=f"\n\nClick here for more info!\nhttps://programer-turtle.github.io/WeatherSystem/Alerts?{FixedID}"

                    if not alert['properties']['certainty'] in ["", "null", None]:
                        PostText+=f"\n\nCertainty\n{alert['properties']['certainty']}"
                        DiscordEmbed["Certainty"] = alert['properties']['certainty']

                    PostText+=f"\n\nDescription\n{alert['properties']['description']}"
                    DiscordEmbed["Description"] = alert['properties']['description']

                    if not alert['properties']['instruction'] in ["", "null", None]:
                        PostText+=f"\n\nInstruction\n{alert['properties']['instruction']}"
                        DiscordEmbed["Instruction"] = alert['properties']['instruction']

                    postID = PostToFacebook(PostText)
                    PostToInstagram(f"\n{PostText}", RadarImageURL)
                    PostToThreads(ThreadsPostText)
                    try:
                        with open(os.path.join(DiscordQueue, f"{postID}.txt"), "w") as file:
                            file.write(str(DiscordEmbed))
                    except:
                        print("Error with discord")
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
            PostToInstagram(f"\n{PostText}", RadarImageURL)
            PostToThreads(PostText)
            try:
                with open(os.path.join(DiscordQueue, f"Today.txt"), "w") as file:
                            file.write(str({"Type":"Forecast", "County":CountyName, "Today":today, "Tonight":tonight}))
            except Exception as e:
                print(f"Error with discord {e}")
                
            today = date.today()
            Christmas = datetime(today.year, 12 ,25)


            if(Christmas.month == today.month) and (today.day <= Christmas.day):
                days = Christmas.day-today.day
                if(days == 0):
                    PostToFacebook("It's Christmas Today!")
                else:
                    PostToFacebook(f"{days} days until Christmas!")
                    

def Main():
    WeatherProcess = multiprocessing.Process(target=MainWeather)
    AlertProcess = multiprocessing.Process(target=MainAlerts)

    WeatherProcess.start()
    AlertProcess.start()

    WeatherProcess.join()
    AlertProcess.join()


if __name__ == "__main__":
    Main()
